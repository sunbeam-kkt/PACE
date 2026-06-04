#!/bin/bash
# Fast DAgger collection template. Keep dataset/model paths aligned with dagger_NYC.sh.

root_dir=.
model_dir=$root_dir/Model/LLaMA-UAV

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
bert_model_path=${BERT_BASE_UNCASED:-$model_dir/model_zoo/bert-base-uncased}
bert_args=(--hf_offline True)
if [ -d "$bert_model_path" ]; then
    bert_args+=(--bert_model_path "$bert_model_path")
fi

CUDA_VISIBLE_DEVICES=0 python -u $root_dir/src/vlnce_src/dagger.py \
    --run_type collect \
    --collect_type dagger \
    --name TravelLLM \
    --gpu_id 4 \
    --simulator_tool_port 25000 \
    --DDP_MASTER_PORT 80002 \
    --batchSize 4 \
    --dagger_it 1 \
    --dagger_p 0.4 \
    --maxWaypoints 200 \
    --activate_maps NYCEnvironmentMegapa \
    --fast_mode True \
    --inference_dtype bf16 \
    --use_amp True \
    --allow_tf32 True \
    --cudnn_benchmark True \
    --merge_lora_for_inference True \
    --empty_cache_each_forward False \
    --assist_dino_interval 5 \
    --assist_dino_cameras frontcamera,downcamera \
    --log_step_interval 5 \
    --verbose_runtime False \
    --dataset_path /mnt/data5/airdrone/dataset/replay_data_log0.1_image0.5/ \
    --dagger_save_path $root_dir/data/dagger_data \
    --model_path $model_dir/work_dirs/llama-vid-7b-pretrain-224-uav-full-data-lora32 \
    --model_base $model_dir/model_zoo/vicuna-7b-v1.5 \
    --vision_tower $model_dir/model_zoo/LAVIS/eva_vit_g.pth \
    --image_processor $model_dir/llamavid/processor/clip-patch14-224 \
    "${bert_args[@]}" \
    --traj_model_path $model_dir/work_dirs/traj_predictor_bs_128_drop_0.1_lr_5e-4 \
    --train_json_path $root_dir/data/uav_dataset/trainset.json \
    --map_spawn_area_json_path $root_dir/data/meta/map_spawnarea_info.json \
    --object_name_json_path $root_dir/data/meta/object_description.json \
    --groundingdino_config $root_dir/src/model_wrapper/utils/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py \
    --groundingdino_model_path $root_dir/src/model_wrapper/utils/GroundingDINO/groundingdino_swint_ogc.pth
