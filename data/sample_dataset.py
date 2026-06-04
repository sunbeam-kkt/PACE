import json
import random
from collections import defaultdict

input_json = ""
output_json = ""

sample_ratio = 0.2  
random.seed(42)      

with open(input_json, 'r') as f:
    data = json.load(f)

print(f"原始样本数: {len(data)}")

key_name = None
for k in ['category', 'scene', 'type', 'camera']:
    if k in data[0]:
        key_name = k
        break

if key_name:
    print(f"按 '{key_name}' 字段分层抽样")
    grouped = defaultdict(list)
    for item in data:
        grouped[item[key_name]].append(item)
    
    subset = []
    for k, group in grouped.items():
        n = max(1, int(len(group) * sample_ratio))
        subset.extend(random.sample(group, n))
else:
    print("未检测到分层字段，使用简单随机抽样")
    subset = random.sample(data, int(len(data) * sample_ratio))

with open(output_json, 'w') as f:
    json.dump(subset, f, indent=2)

print(f"抽样后样本数: {len(subset)}")
print(f"保存到: {output_json}")
