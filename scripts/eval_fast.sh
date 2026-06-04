#!/bin/bash
# Fast evaluation template. Keep dataset/model paths aligned with eval.sh.

root_dir=./
model_dir=$root_dir/Model/LLaMA-UAV

eval_cuda_visible_devices=${EVAL_CUDA_VISIBLE_DEVICES:-${CUDA_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}}
gpu_id=${GPU_ID:-0,1,2,3,4,5,6,7}
dataset_path=${DATASET_PATH:-$model_dir/dataset}
eval_save_path=${EVAL_SAVE_PATH:-$root_dir/outputs/eval_closeloop/eval_test}
model_path=${MODEL_PATH:-$model_dir/work_dirs/llama-vid-7b-pretrain-224-uav-full-data-lora32-initial}
batch_size=${EVAL_BATCH_SIZE:-4}
max_waypoints=${MAX_WAYPOINTS:-200}

if [ "${DISABLE_EXTERNAL_ASSISTANT:-False}" = "True" ] || [ "${USE_INTERNALIZED_ASSISTANT:-False}" = "True" ]; then
    always_help=${ALWAYS_HELP:-False}
    use_gt=${USE_GT:-False}
else
    always_help=${ALWAYS_HELP:-True}
    use_gt=${USE_GT:-True}
fi

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
bert_model_path=${BERT_BASE_UNCASED:-$model_dir/model_zoo/bert-base-uncased}
bert_args=(--hf_offline True)
if [ -d "$bert_model_path" ]; then
    bert_args+=(--bert_model_path "$bert_model_path")
fi

innovation_args=(
    --use_internalized_assistant "${USE_INTERNALIZED_ASSISTANT:-False}"
    --disable_external_assistant "${DISABLE_EXTERNAL_ASSISTANT:-False}"
    --use_counterfactual_grounding "${USE_COUNTERFACTUAL_GROUNDING:-False}"
    --use_affordance_field "${USE_AFFORDANCE_FIELD:-False}"
)
if [ -n "${INNOVATION_TRACE_PATH:-}" ]; then
    mkdir -p "$(dirname "$INNOVATION_TRACE_PATH")"
    rm -f "$INNOVATION_TRACE_PATH"
    innovation_args+=(
        --innovation_trace_path "$INNOVATION_TRACE_PATH"
        --innovation_trace_max_records "${INNOVATION_TRACE_MAX_RECORDS:-120}"
        --innovation_trace_stride "${INNOVATION_TRACE_STRIDE:-5}"
        --innovation_trace_include_affordance_field "${INNOVATION_TRACE_INCLUDE_AFFORDANCE_FIELD:-True}"
    )
fi

CUDA_VISIBLE_DEVICES=$eval_cuda_visible_devices python -u $root_dir/src/vlnce_src/eval.py \
    --run_type eval \
    --name TravelLLM \
    --gpu_id "$gpu_id" \
    --simulator_tool_port 30000 \
    --DDP_MASTER_PORT 80005 \
    --batchSize "$batch_size" \
    --always_help "$always_help" \
    --use_gt "$use_gt" \
    --maxWaypoints "$max_waypoints" \
    --fast_mode True \
    --inference_dtype bf16 \
    --use_amp True \
    --allow_tf32 True \
    --cudnn_benchmark True \
    --merge_lora_for_inference True \
    --empty_cache_each_forward False \
    --done_detection_interval 5 \
    --log_step_interval 5 \
    --verbose_runtime False \
    --dataset_path "$dataset_path" \
    --eval_save_path "$eval_save_path" \
    --model_path "$model_path" \
    --model_base $model_dir/model_zoo/vicuna-7b-v1.5 \
    --vision_tower $model_dir/model_zoo/LAVIS/eva_vit_g.pth \
    --image_processor $model_dir/llamavid/processor/clip-patch14-224 \
    "${bert_args[@]}" \
    --traj_model_path $model_dir/work_dirs/traj_predictor_bs_128_drop_0.1_lr_5e-4 \
    --eval_json_path $root_dir/data/uav_dataset/seen_valset.json \
    --map_spawn_area_json_path $root_dir/data/meta/map_spawnarea_info.json \
    --object_name_json_path $root_dir/data/meta/object_description.json \
    --groundingdino_config $root_dir/src/model_wrapper/utils/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py \
    --groundingdino_model_path $root_dir/src/model_wrapper/utils/GroundingDINO/groundingdino_swint_ogc.pth \
    "${innovation_args[@]}"
