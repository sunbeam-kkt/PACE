#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path


W, H = 1680, 720


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-float(x)))


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, float(v)))


def hex_to_rgb(c):
    c = c.strip("#")
    return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#" + "".join(f"{int(clamp(x, 0, 255)):02x}" for x in rgb)


def mix(a, b, t):
    ar, ag, ab = hex_to_rgb(a)
    br, bg, bb = hex_to_rgb(b)
    return rgb_to_hex((ar + (br - ar) * t, ag + (bg - ag) * t, ab + (bb - ab) * t))


def score_color(t):
    t = clamp(t)
    if t < 0.5:
        return mix("#d84e3f", "#f2c84b", t / 0.5)
    return mix("#f2c84b", "#087b25", (t - 0.5) / 0.5)


def norm_scores(values):
    if not values:
        return []
    lo, hi = min(values), max(values)
    if abs(hi - lo) < 1e-9:
        return [0.55 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def as_points(value):
    if value is None:
        return []
    if len(value) == 0:
        return []
    if isinstance(value[0], (int, float)):
        return [value[:3]]
    return [p[:3] for p in value if isinstance(p, list) and len(p) >= 3]


def world_to_local(points, current_position):
    if not points:
        return []
    if current_position is None:
        return points
    return [[p[0] - current_position[0], p[1] - current_position[1], p[2] - current_position[2]] for p in points]


def trajectory_tokens(local_points):
    pts = [[0.0, 0.0, 0.0]] + local_points
    tokens = []
    last_yaw = 0.0
    for a, b in zip(pts[:-1], pts[1:]):
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        yaw = math.atan2(dy, dx) if abs(dx) + abs(dy) > 1e-6 else last_yaw
        dpsi = yaw - last_yaw
        rho = math.sqrt(dx * dx + dy * dy + dz * dz)
        tokens.append([dx, dy, dz, dpsi, rho])
        last_yaw = yaw
    return tokens


def primitive_score_from_field(candidate, grid, field):
    if not grid or not field:
        return 0.0
    best_idx = 0
    best_dist = float("inf")
    for i, p in enumerate(grid):
        d = (p[0] - candidate[0]) ** 2 + (p[1] - candidate[1]) ** 2 + (p[2] - candidate[2]) ** 2
        if d < best_dist:
            best_idx, best_dist = i, d
    ch = [sigmoid(x) for x in field[best_idx]]
    return 1.2 * ch[0] + 1.0 * ch[1] + 1.4 * ch[2] + 1.6 * ch[3] + 0.3 * ch[4] - 1.0 * ch[5]


class SVG:
    def __init__(self):
        self.e = []

    def add(self, s):
        self.e.append(s)

    def text(self, x, y, text, size=16, fill="#111111", weight="400", anchor="start"):
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" text-anchor="{anchor}" '
            f'style="font-family:Arial,Helvetica,sans-serif;font-size:{size}px;font-weight:{weight}">{escape(text)}</text>'
        )

    def rect(self, x, y, w, h, fill="#ffffff", stroke="#333333", sw=1.0, rx=8, opacity=1.0):
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"/>'
        )

    def line(self, x1, y1, x2, y2, stroke="#333333", sw=1.5, arrow=False, dash="", opacity=1.0):
        marker = ' marker-end="url(#arrow)"' if arrow else ""
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}" opacity="{opacity}" stroke-linecap="round"{dash_attr}{marker}/>'
        )

    def path(self, pts, stroke="#333333", sw=2.0, arrow=False, dash="", opacity=1.0):
        if len(pts) < 2:
            return
        d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        marker = ' marker-end="url(#arrow)"' if arrow else ""
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}" '
            f'stroke-linejoin="round" stroke-linecap="round"{dash_attr}{marker}/>'
        )

    def circle(self, x, y, r, fill="#ffffff", stroke="#333333", sw=1.0, opacity=1.0):
        self.add(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" opacity="{opacity}"/>'
        )

    def polygon(self, pts, fill="#ffffff", stroke="#333333", sw=1.0, opacity=1.0):
        points = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.add(f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"/>')

    def save(self, path):
        head = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/>
  </marker>
</defs>
<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>
'''
        Path(path).write_text(head + "\n".join(self.e) + "\n</svg>\n", encoding="utf-8")


def escape(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def project3(p, ox=650, oy=520, sx=8.6, sy=4.8, sz=11.0):
    x, y, z = p
    return ox + sx * x + sy * y, oy - sz * z + sy * y


def map2d(p, x0, y0, scale=12.0):
    return x0 + p[0] * scale, y0 - p[1] * scale


def draw_panel_a(svg, record, local_traj, tokens):
    x0, y0, w, h = 30, 55, 500, 585
    svg.rect(x0, y0, w, h, "#fbfdff", "#2b65be", 1.4, 14)
    svg.text(x0 + 22, y0 + 35, "(a) Real refined trajectory → vector tokens", 20, "#0b49b6", "700")
    svg.text(x0 + 22, y0 + 62, f"episode: {record.get('episode_id', '-')}, step: {record.get('step', '-')}", 13, "#4b5563")

    cx, cy = x0 + 245, y0 + 335
    for k in range(-4, 5):
        svg.line(cx + k * 55, y0 + 105, cx + k * 55, y0 + 455, "#e5e9f1", 1)
        svg.line(x0 + 55, cy + k * 55, x0 + 455, cy + k * 55, "#e5e9f1", 1)
    svg.line(x0 + 55, cy, x0 + 455, cy, "#b5c3d6", 1.2, True)
    svg.line(cx, y0 + 455, cx, y0 + 105, "#b5c3d6", 1.2, True)

    pts = [map2d([0, 0, 0], cx, cy)] + [map2d(p, cx, cy) for p in local_traj]
    svg.path(pts, "#087b25", 4.0, True)
    for idx, p in enumerate(pts):
        svg.circle(p[0], p[1], 6.0, "#087b25" if idx else "#18449b", "white", 1.5)
        if idx > 0:
            svg.text(p[0] + 8, p[1] - 8, f"v{idx}", 12, "#0b49b6", "700")

    sel = record.get("selected_local_waypoint")
    if sel:
        sx, sy = map2d(sel, cx, cy)
        svg.circle(sx, sy, 10, "#ffb000", "#7a4f00", 1.2)
        svg.text(sx + 12, sy - 8, "selected subgoal", 12, "#9a5a00", "700")
        svg.line(cx, cy, sx, sy, "#ffb000", 1.5, True, "6 5")

    svg.rect(x0 + 42, y0 + 475, 416, 118, "#ffffff", "#6e99d4", 1.0, 10)
    svg.text(x0 + 62, y0 + 505, "Vectorized from real trajectory:", 15, "#111111", "700")
    svg.text(x0 + 62, y0 + 534, "vₖ = [Δxₖ, Δyₖ, Δzₖ, Δψₖ, ρₖ]", 19, "#111111")
    if tokens:
        t0 = tokens[min(1, len(tokens) - 1)]
        svg.text(x0 + 62, y0 + 565, f"example token: [{t0[0]:.2f}, {t0[1]:.2f}, {t0[2]:.2f}, {t0[3]:.2f}, {t0[4]:.2f}]", 13, "#4b5563")


def draw_panel_b(svg, record):
    x0, y0, w, h = 560, 55, 610, 585
    svg.rect(x0, y0, w, h, "#fffefe", "#087b25", 1.4, 14)
    svg.text(x0 + 22, y0 + 35, "(b) Real predicted local affordance field", 20, "#087b25", "700")
    svg.text(x0 + 22, y0 + 62, "voxel color = weighted sigmoid channels from the model head", 13, "#4b5563")

    grid = record.get("local_grid") or []
    field = record.get("affordance_field_logits") or []
    cell_scores = []
    for ch in field:
        if len(ch) >= 6:
            vals = [sigmoid(v) for v in ch[:6]]
            cell_scores.append(1.2 * vals[0] + vals[1] + 1.4 * vals[2] + 1.6 * vals[3] + 0.3 * vals[4] - vals[5])
    nscore = norm_scores(cell_scores)
    threshold = sorted(nscore)[max(0, int(len(nscore) * 0.58))] if nscore else 1.0

    # Grid box.
    corners = [(-20, -20, -8), (20, -20, -8), (20, 20, -8), (-20, 20, -8), (-20, -20, 8), (20, -20, 8), (20, 20, 8), (-20, 20, 8)]
    pc = [project3(c, x0 + 255, y0 + 460) for c in corners]
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]:
        svg.line(*pc[a], *pc[b], "#8fb0d4", 1.0)

    for p, t in zip(grid, nscore):
        if t < threshold:
            continue
        px, py = project3(p, x0 + 255, y0 + 460)
        color = mix("#2d82c7", "#ffb000", t)
        svg.rect(px - 8, py - 8, 16, 16, color, "none", 0, 2, 0.42)

    svg.polygon([(x0 + 245, y0 + 448), (x0 + 265, y0 + 448), (x0 + 255, y0 + 428)], "#18449b", "white", 1.2)
    svg.text(x0 + 270, y0 + 438, "current UAV", 12, "#18449b", "700")

    candidates = record.get("candidate_waypoints") or []
    candidate_scores = record.get("candidate_scores") or []
    if not candidate_scores and field and grid:
        candidate_scores = [primitive_score_from_field(c[:3], grid, field) for c in candidates]
    ns = norm_scores(candidate_scores)
    for i, cand in enumerate(candidates):
        if len(cand) < 3:
            continue
        color = score_color(ns[i] if i < len(ns) else 0.5)
        end = project3(cand[:3], x0 + 255, y0 + 460)
        start = project3((0, 0, 0), x0 + 255, y0 + 460)
        best = i == (candidate_scores.index(max(candidate_scores)) if candidate_scores else -1)
        svg.line(*start, *end, color, 4.0 if best else 2.2, True, opacity=1.0 if best else 0.55)
        svg.circle(end[0], end[1], 5.2, color, "white", 1)
        svg.text(end[0] + 7, end[1] - 5, f"π{i+1}", 12, color, "700")

    selected = record.get("affordance_selected_local") or record.get("selected_local_waypoint")
    if selected:
        sx, sy = project3(selected[:3], x0 + 255, y0 + 460)
        svg.circle(sx, sy, 12, "#087b25", "white", 2)
        svg.text(sx + 14, sy - 9, "π*", 16, "#087b25", "700")

    svg.rect(x0 + 402, y0 + 442, 170, 112, "#ffffff", "#777777", 1.0, 8)
    svg.text(x0 + 418, y0 + 472, "6 predicted channels", 13, "#111111", "700")
    labels = ["flyability", "clearance", "observability", "relevance", "landing", "cost"]
    colors = ["#2d6bcb", "#1ea2a4", "#7b3bbe", "#ff4b23", "#188c35", "#505050"]
    for i, (lab, col) in enumerate(zip(labels, colors)):
        svg.circle(x0 + 423, y0 + 493 + i * 14, 4.5, col, "none", 0)
        svg.text(x0 + 434, y0 + 498 + i * 14, lab, 10.5, col, "700")


def draw_panel_c(svg, record, tokens):
    x0, y0, w, h = 1200, 55, 450, 585
    svg.rect(x0, y0, w, h, "#fffdfd", "#d84e3f", 1.4, 14)
    svg.text(x0 + 22, y0 + 35, "(c) Real token / score table", 20, "#d84e3f", "700")

    candidates = record.get("candidate_waypoints") or []
    scores = record.get("candidate_scores") or []
    rejections = record.get("candidate_rejection_logits") or []
    if candidates and not scores:
        scores = [0.0] * len(candidates)
    if rejections and scores:
        scores = [s - sigmoid(r) for s, r in zip(scores, rejections)]
    ns = norm_scores(scores)
    best = scores.index(max(scores)) if scores else -1

    headers = ["Δx", "Δy", "Δz", "score"]
    tx, ty = x0 + 38, y0 + 102
    widths = [58, 58, 58, 78]
    svg.text(tx, ty - 18, "candidate primitives", 14, "#111111", "700")
    x = tx + 58
    for head, ww in zip(headers, widths):
        svg.text(x + ww / 2, ty + 10, head, 13, "#111111", "700", "middle")
        x += ww
    for i, cand in enumerate(candidates[:8]):
        yy = ty + 25 + i * 38
        svg.text(tx + 6, yy + 23, f"π{i+1}", 14, "#111111", "700")
        vals = cand[:3] + ([scores[i]] if i < len(scores) else [0.0])
        x = tx + 58
        for val, ww in zip(vals, widths):
            t = ns[i] if i < len(ns) else 0.5
            fill = mix("#fff5f5", "#d9f3df", t)
            svg.rect(x, yy, ww - 4, 30, fill, "white", 1, 4)
            svg.text(x + ww / 2 - 2, yy + 20, f"{val:.2f}", 10, "#111111", "400", "middle")
            x += ww
        label = "keep" if i == best else "reject"
        color = "#087b25" if i == best else "#c62828"
        svg.text(tx + 330, yy + 20, label, 12, color, "700")

    svg.rect(x0 + 38, y0 + 455, 370, 108, "#ffffff", "#087b25", 1.0, 10)
    svg.text(x0 + 55, y0 + 486, "Trajectory vector tokens from real refinement:", 14, "#111111", "700")
    svg.text(x0 + 55, y0 + 516, "vₖ = [Δxₖ, Δyₖ, Δzₖ, Δψₖ, ρₖ]", 17, "#111111")
    if tokens:
        shown = tokens[:3]
        txt = " ; ".join(f"[{v[0]:.1f},{v[1]:.1f},{v[2]:.1f},{v[3]:.2f},{v[4]:.1f}]" for v in shown)
        svg.text(x0 + 55, y0 + 545, txt[:62], 11, "#4b5563")

    help_action = record.get("help_action")
    if help_action is not None:
        svg.text(x0 + 38, y0 + 610, f"internal help: {help_action}, gate={record.get('help_gate', 0):.2f}", 14, "#0b49b6", "700")


def choose_record(records, args):
    candidates = records
    if args.episode_id:
        candidates = [r for r in candidates if str(r.get("episode_id")) == str(args.episode_id)]
    if args.step is not None:
        candidates = [r for r in candidates if int(r.get("step", -1)) == int(args.step)]
    if args.record_index is not None:
        return candidates[int(args.record_index)]
    scored = []
    for r in candidates:
        score = 0
        score += 4 if r.get("affordance_field_logits") else 0
        score += 3 if r.get("candidate_scores") else 0
        score += 2 if r.get("refined_world_trajectory") else 0
        score += 1 if r.get("selected_local_waypoint") else 0
        scored.append((score, r))
    if not scored:
        raise RuntimeError("No matching records found in trace.")
    return sorted(scored, key=lambda x: x[0], reverse=True)[0][1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", required=True, help="JSONL generated by --innovation_trace_path during eval")
    parser.add_argument("--output", default=None, help="output SVG path")
    parser.add_argument("--episode-id", default=None)
    parser.add_argument("--step", type=int, default=None)
    parser.add_argument("--record-index", type=int, default=None)
    args = parser.parse_args()

    records = []
    with open(args.trace, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    if not records:
        raise RuntimeError(f"Empty trace: {args.trace}")

    record = choose_record(records, args)
    refined = as_points(record.get("refined_world_trajectory"))
    current = record.get("current_position")
    local_traj = world_to_local(refined, current)
    if not local_traj:
        local_traj = as_points(record.get("selected_local_waypoint"))
    tokens = trajectory_tokens(local_traj)

    svg = SVG()
    svg.text(W / 2, 32, "Real Experiment Visualization: Vectorized Aerial Information-Trajectory Affordance Planning", 24, "#111111", "700", "middle")
    draw_panel_a(svg, record, local_traj, tokens)
    draw_panel_b(svg, record)
    draw_panel_c(svg, record, tokens)

    output = args.output
    if output is None:
        trace_path = Path(args.trace)
        output = trace_path.with_name(f"{trace_path.stem}_real_affordance_vectorization.svg")
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    svg.save(output)
    print(f"Saved {output}")
    print(f"Used episode_id={record.get('episode_id')} step={record.get('step')} batch_index={record.get('batch_index')}")


if __name__ == "__main__":
    main()
