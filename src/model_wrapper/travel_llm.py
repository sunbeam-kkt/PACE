import numpy as np
import torch
import json
import os
from contextlib import nullcontext
from src.model_wrapper.base_model import BaseModelWrapper
from src.model_wrapper.utils.travel_util import *
from src.common.param import args
from llamavid.model.uav_innovation import build_local_grid

class TravelModelWrapper(BaseModelWrapper):
    def __init__(self, model_args, data_args):
        self.tokenizer, self.model, self.image_processor = load_model(model_args)
        self.traj_model = load_traj_model(model_args)
        self.inference_dtype = self._resolve_dtype(args.inference_dtype)
        self.model.to(dtype=self.inference_dtype)
        self.traj_model.to(dtype=self.inference_dtype, device=self.model.device)
        self.dino_moinitor = None
        self.model_args = model_args
        self.data_args = data_args
        self.use_amp = bool(args.use_amp)
        self.done_detection_interval = int(args.done_detection_interval)
        self._non_blocking = self.model.device.type == 'cuda'
        self.last_innovation_outputs = {}
        self.last_llm_waypoints_raw = None
        self.last_selected_local_waypoints = None
        self.last_candidate_choices = None
        self.last_affordance_choices = None
        self._innovation_trace_count = 0
        self.eval()

    @staticmethod
    def _resolve_dtype(dtype_name):
        dtype_name = str(dtype_name).lower()
        if dtype_name in ["fp16", "float16", "half"]:
            return torch.float16
        if dtype_name in ["fp32", "float32"]:
            return torch.float32
        return torch.bfloat16

    def _amp_context(self):
        if not self.use_amp or self.model.device.type != 'cuda':
            return nullcontext()
        return torch.autocast(device_type='cuda', dtype=self.inference_dtype)

    def prepare_inputs(self, episodes, target_positions, assist_notices=None):
        inputs = []
        rot_to_targets = []
        
        for i in range(len(episodes)):
            input_item, rot_to_target = prepare_data_to_inputs(
                episodes=episodes[i],
                tokenizer=self.tokenizer,
                image_processor=self.image_processor,
                data_args=self.data_args,
                target_point=target_positions[i],
                assist_notice=assist_notices[i] if assist_notices is not None else None,
                disable_external_assistant=bool(args.disable_external_assistant or args.selfhelp_dagger or args.use_internalized_assistant)
            )
            inputs.append(input_item)
            rot_to_targets.append(rot_to_target)
        batch = inputs_to_batch(tokenizer=self.tokenizer, instances=inputs)

        inputs_device = {k: v.to(self.model.device, non_blocking=self._non_blocking) for k, v in batch.items() 
            if 'prompts' not in k and 'images' not in k and 'historys' not in k}
        inputs_device['prompts'] = [item for item in batch['prompts']]
        inputs_device['images'] = [item.to(self.model.device, non_blocking=self._non_blocking) for item in batch['images']]
        inputs_device['historys'] = [item.to(device=self.model.device, dtype=self.model.dtype, non_blocking=self._non_blocking) for item in batch['historys']]
        inputs_device['orientations'] = inputs_device['orientations'].to(dtype=self.model.dtype)
        inputs_device['return_waypoints'] = True
        inputs_device['return_innovation_outputs'] = bool(args.use_counterfactual_grounding or args.use_affordance_field or args.use_internalized_assistant)
        if args.use_counterfactual_grounding or args.use_affordance_field:
            inputs_device['candidate_waypoints'] = self._build_candidate_waypoints(rot_to_targets, target_positions, len(episodes))
        inputs_device['use_cache'] = bool(args.llm_use_cache)
        
        return inputs_device, rot_to_targets

    def run_llm_model(self, inputs):
        with torch.inference_mode(), self._amp_context():
            outputs = self.model(**inputs)
            if isinstance(outputs, dict):
                waypoints_tensor = outputs["waypoints"]
                self.last_innovation_outputs = {
                    key: value.detach().cpu()
                    for key, value in outputs.items()
                    if torch.is_tensor(value)
                }
            else:
                waypoints_tensor = outputs
                self.last_innovation_outputs = {}
            waypoints_llm = waypoints_tensor.detach().cpu().to(dtype=torch.float32).numpy()
            candidate_tensor = self._select_candidate_waypoints(outputs) if isinstance(outputs, dict) else None
            affordance_tensor = self._plan_from_affordance(outputs) if isinstance(outputs, dict) else None
            candidate_choices = candidate_tensor.cpu().to(dtype=torch.float32).numpy() if candidate_tensor is not None else None
            affordance_choices = affordance_tensor.cpu().to(dtype=torch.float32).numpy() if affordance_tensor is not None else None
        self.last_llm_waypoints_raw = waypoints_llm
        self.last_candidate_choices = candidate_choices
        self.last_affordance_choices = affordance_choices
        waypoints_llm_new = []
        for idx, waypoint in enumerate(waypoints_llm):
            if affordance_choices is not None:
                waypoint_new = affordance_choices[idx]
            elif candidate_choices is not None:
                waypoint_new = candidate_choices[idx]
            else:
                waypoint_new = waypoint[:3] / (1e-6 + np.linalg.norm(waypoint[:3])) * waypoint[3]
            waypoints_llm_new.append(waypoint_new)
        self.last_selected_local_waypoints = np.array(waypoints_llm_new)
        return self.last_selected_local_waypoints

    def _select_candidate_waypoints(self, outputs):
        if not args.use_counterfactual_grounding or "candidate_scores" not in outputs or "candidate_waypoints" not in outputs:
            return None
        scores = outputs["candidate_scores"]
        rejections = outputs.get("candidate_rejection_logits")
        if rejections is not None:
            scores = scores - torch.sigmoid(rejections)
        best_idx = torch.argmax(scores, dim=-1)
        return outputs["candidate_waypoints"][torch.arange(best_idx.shape[0], device=best_idx.device), best_idx]

    def _plan_from_affordance(self, outputs):
        if not args.use_affordance_field or "affordance_field" not in outputs:
            return None
        field = outputs["affordance_field"]
        grid = build_local_grid(field.device, field.dtype)
        flyability = torch.sigmoid(field[..., 0])
        clearance = torch.sigmoid(field[..., 1])
        observability = torch.sigmoid(field[..., 2])
        target_likelihood = torch.sigmoid(field[..., 3])
        landing_suitability = torch.sigmoid(field[..., 4])
        control_cost = torch.sigmoid(field[..., 5])
        score = (
            1.2 * flyability
            + 1.0 * clearance
            + 1.4 * observability
            + 1.6 * target_likelihood
            + 0.3 * landing_suitability
            - 1.0 * control_cost
        )
        best_idx = torch.argmax(score, dim=-1)
        return grid[best_idx]

    def _build_candidate_waypoints(self, rot_to_targets, target_positions, batch_size):
        candidates = []
        base_distance = 12.0
        for _ in range(batch_size):
            candidates.append([
                [base_distance, 0.0, 0.0],
                [base_distance, -6.0, 0.0],
                [base_distance, 6.0, 0.0],
                [base_distance, 0.0, 4.0],
                [base_distance, 0.0, -4.0],
                [base_distance * 0.5, 0.0, 0.0],
            ])
        return torch.tensor(candidates, dtype=self.model.dtype, device=self.model.device)

    def run_traj_model(self, episodes, waypoints_llm_new, rot_to_targets):
        inputs = prepare_data_to_traj_model(episodes, waypoints_llm_new, self.image_processor, rot_to_targets)
        with torch.inference_mode(), self._amp_context():
            waypoints_traj = self.traj_model(inputs, None)
        refined_waypoints = waypoints_traj.detach().cpu().to(dtype=torch.float32).numpy()
        refined_waypoints = transform_to_world(refined_waypoints, episodes)
        return refined_waypoints
    
    def eval(self):
        self.model.eval()
        self.traj_model.eval()
        
    def run(self, inputs, episodes, rot_to_targets):
        waypoints_llm_new = self.run_llm_model(inputs)
        refined_waypoints = self.run_traj_model(episodes, waypoints_llm_new, rot_to_targets)
        return refined_waypoints

    @staticmethod
    def _jsonable(value, batch_index=None):
        if value is None:
            return None
        if torch.is_tensor(value):
            value = value.detach().cpu().to(dtype=torch.float32).numpy()
        value = np.asarray(value) if isinstance(value, (list, tuple)) else value
        if isinstance(value, np.ndarray):
            if batch_index is not None and value.ndim > 0:
                value = value[batch_index]
            return value.astype(float).tolist()
        if isinstance(value, (np.floating, np.integer)):
            return value.item()
        return value

    @staticmethod
    def _episode_position(episode):
        return episode[-1]["sensors"]["state"]["position"]

    @staticmethod
    def _episode_rotation(episode):
        imu = episode[-1]["sensors"].get("imu", {})
        return imu.get("rotation")

    def maybe_write_innovation_trace(self, step, batch_state, refined_waypoints):
        trace_path = getattr(args, "innovation_trace_path", None)
        if trace_path is None or str(trace_path).strip() == "":
            return
        stride = max(1, int(getattr(args, "innovation_trace_stride", 1)))
        if int(step) % stride != 0:
            return
        max_records = int(getattr(args, "innovation_trace_max_records", 200))
        if max_records > 0 and self._innovation_trace_count >= max_records:
            return

        trace_path = os.path.abspath(os.path.expanduser(str(trace_path)))
        os.makedirs(os.path.dirname(trace_path), exist_ok=True)
        outputs = self.last_innovation_outputs or {}
        grid = build_local_grid(torch.device("cpu"), torch.float32).numpy()
        help_action_names = ["none", "cruise", "left", "right", "takeoff", "landing"]

        with open(trace_path, "a", encoding="utf-8") as f:
            for i, episode in enumerate(batch_state.episodes):
                if max_records > 0 and self._innovation_trace_count >= max_records:
                    break
                if len(episode) == 0:
                    continue
                record = {
                    "step": int(step),
                    "batch_index": int(i),
                    "episode_id": os.path.basename(str(batch_state.ori_data_dirs[i]).rstrip("/\\")),
                    "trajectory_dir": str(batch_state.ori_data_dirs[i]),
                    "object_info": batch_state.object_infos[i],
                    "current_position": self._episode_position(episode),
                    "current_rotation": self._episode_rotation(episode),
                    "target_position": self._jsonable(batch_state.target_positions[i]),
                    "distance_to_target": float(batch_state.distance_to_ends[i][-1]) if batch_state.distance_to_ends[i] else None,
                    "selected_local_waypoint": self._jsonable(self.last_selected_local_waypoints, i),
                    "llm_waypoint_raw": self._jsonable(self.last_llm_waypoints_raw, i),
                    "candidate_selected_local": self._jsonable(self.last_candidate_choices, i),
                    "affordance_selected_local": self._jsonable(self.last_affordance_choices, i),
                    "refined_world_trajectory": self._jsonable(refined_waypoints, i),
                    "local_grid": grid.astype(float).tolist(),
                }
                if "candidate_waypoints" in outputs:
                    record["candidate_waypoints"] = self._jsonable(outputs["candidate_waypoints"], i)
                if "candidate_scores" in outputs:
                    record["candidate_scores"] = self._jsonable(outputs["candidate_scores"], i)
                if "candidate_rejection_logits" in outputs:
                    record["candidate_rejection_logits"] = self._jsonable(outputs["candidate_rejection_logits"], i)
                if getattr(args, "innovation_trace_include_affordance_field", True) and "affordance_field" in outputs:
                    record["affordance_field_logits"] = self._jsonable(outputs["affordance_field"], i)
                if "help_gate_logits" in outputs:
                    gate_logit = float(np.asarray(self._jsonable(outputs["help_gate_logits"], i)).reshape(-1)[0])
                    record["help_gate"] = 1.0 / (1.0 + np.exp(-gate_logit))
                    record["help_gate_logit"] = gate_logit
                if "help_action_logits" in outputs:
                    logits = np.asarray(self._jsonable(outputs["help_action_logits"], i), dtype=np.float64)
                    logits = logits - logits.max()
                    probs = np.exp(logits) / np.maximum(np.exp(logits).sum(), 1e-8)
                    action_id = int(probs.argmax())
                    record["help_action_probs"] = probs.astype(float).tolist()
                    record["help_action"] = help_action_names[action_id]
                if "help_severity" in outputs:
                    record["help_severity"] = float(np.asarray(self._jsonable(outputs["help_severity"], i)).reshape(-1)[0])
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                self._innovation_trace_count += 1
    
    def predict_done(self, episodes, object_infos):
        if self.done_detection_interval <= 0:
            return [False for _ in range(len(episodes))]
        prediction_dones = []
        if self.dino_moinitor is None:
            from src.vlnce_src.dino_monitor_online import DinoMonitor
            self.dino_moinitor = DinoMonitor.get_instance()
        for i in range(len(episodes)):
            prediction_done = self.dino_moinitor.get_dino_results(episodes[i], object_infos[i])
            prediction_dones.append(prediction_done)
        return prediction_dones

    def should_predict_done(self, step):
        return self.done_detection_interval > 0 and step % self.done_detection_interval == 0
        

    
