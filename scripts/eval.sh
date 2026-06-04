#!/bin/bash
# change the dataset_path to your own path

root_dir=. # TravelUAV directory
model_dir=$root_dir/Model/LLaMA-UAV

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
bert_model_path=${BERT_BASE_UNCASED:-$model_dir/model_zoo/bert-base-uncased}
bert_args=(--hf_offline True)
if [ -d "$bert_model_path" ]; then
    bert_args+=(--bert_model_path "$bert_model_path")
fi


CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python -u $root_dir/src/vlnce_src/eval.py \
    --run_type eval \
    --name TravelLLM \
    --gpu_id 0,1,2,3,4,5,6,7 \
    --simulator_tool_port 30000 \
    --DDP_MASTER_PORT 80005 \
    --batchSize 4 \
    --always_help True \
    --use_gt True \
    --maxWaypoints 200 \
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
    --dataset_path . \
    --eval_save_path . \
    --model_path $model_dir/work_dirs/llama-vid-7b-pretrain-224-uav-full-data-lora32 \
    --model_base $model_dir/model_zoo/vicuna-7b-v1.5 \
    --vision_tower $model_dir/model_zoo/LAVIS/eva_vit_g.pth \
    --image_processor $model_dir/llamavid/processor/clip-patch14-224 \
    "${bert_args[@]}" \
    --traj_model_path $model_dir/work_dirs/traj_predictor_bs_128_drop_0.1_lr_5e-4 \
    --eval_json_path $root_dir/data/uav_dataset/seen_valset.json \
    --map_spawn_area_json_path $root_dir/data/meta/map_spawnarea_info.json \
    --object_name_json_path $root_dir/data/meta/object_description.json \
    --groundingdino_config $root_dir/src/model_wrapper/utils/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py \
    --groundingdino_model_path $root_dir/src/model_wrapper/utils/GroundingDINO/groundingdino_swint_ogc.pth
