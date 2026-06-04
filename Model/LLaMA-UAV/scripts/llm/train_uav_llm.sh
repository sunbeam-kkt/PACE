#!/bin/bash
# change DATASET_PATH / OUTPUT_DIR from the command line when needed.

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
model_dir="$(cd "$script_dir/../.." && pwd)"
root_dir="$(cd "$model_dir/../.." && pwd)"

export HF_HUB_OFFLINE=${HF_HUB_OFFLINE:-1}
export TRANSFORMERS_OFFLINE=${TRANSFORMERS_OFFLINE:-1}
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-max_split_size_mb:128}
export WANDB_MODE=${WANDB_MODE:-offline}

DATASET_PATH=${DATASET_PATH:-/path/to/dataset/}
OUTPUT_DIR=${OUTPUT_DIR:-$model_dir/work_dirs/llama-vid-7b-pretrain-224-uav-full-data-lora32-innov}
MASTER_PORT=${MASTER_PORT:-29101}
DS_CONFIG=${DS_CONFIG:-$model_dir/scripts/zero2_offload.json}
PER_DEVICE_BS=${PER_DEVICE_BS:-2}
GRAD_ACCUM=${GRAD_ACCUM:-8}
LORA_R=${LORA_R:-16}
LORA_ALPHA=${LORA_ALPHA:-32}
DATALOADER_WORKERS=${DATALOADER_WORKERS:-2}
MAX_STEPS=${MAX_STEPS:-5000}
MODEL_MAX_LENGTH=${MODEL_MAX_LENGTH:-1024}
SAVE_STEPS=${SAVE_STEPS:-500}

ds_args=(--master_port "$MASTER_PORT")
if [ -n "${DS_INCLUDE:-}" ]; then
    ds_args+=(--include "$DS_INCLUDE")
fi

export PYTHONPATH="$model_dir:${PYTHONPATH:-}"

deepspeed \
    "${ds_args[@]}" \
    $model_dir/llamavid/train/train_uav/train_uav_notice.py \
    --data_path $root_dir/data/uav_dataset/trainset.json \
    --dataset_path $DATASET_PATH \
    --output_dir $OUTPUT_DIR \
    --deepspeed $DS_CONFIG \
    --model_name_or_path $model_dir/model_zoo/vicuna-7b-v1.5/ \
    --version imgsp_uav \
    --is_multimodal True \
    --vision_tower $model_dir/model_zoo/LAVIS/eva_vit_g.pth \
    --image_processor $model_dir/llamavid/processor/clip-patch14-224 \
    --mm_projector_type mlp2x_gelu \
    --tune_mm_mlp_adapter True \
    --tune_waypoint_predictor True \
    --mm_vision_select_layer -2 \
    --mm_use_im_start_end False \
    --mm_use_im_patch_token False \
    --video_fps 1 \
    --bert_type "qformer_pretrain_freeze" \
    --num_query 32 \
    --pretrain_qformer $model_dir/model_zoo/LAVIS/instruct_blip_vicuna7b_trimmed.pth \
    --compress_type "mean" \
    --use_internalized_assistant True \
    --use_counterfactual_grounding True \
    --use_affordance_field True \
    --internalize_assistant True \
    --help_loss_scale 0.2 \
    --ranking_loss_scale 0.2 \
    --rejection_loss_scale 0.1 \
    --affordance_loss_scale 0.1 \
    --distillation_loss_scale 0.1 \
    --innovation_hidden_dim 512 \
    --freeze_token_embeddings True \
    --freeze_lm_head True \
    --freeze_mm_projector True \
    --freeze_vlm_attention True \
    --bf16 True \
    --num_train_epochs 2 \
    --max_steps $MAX_STEPS \
    --per_device_train_batch_size $PER_DEVICE_BS \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps $GRAD_ACCUM \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps $SAVE_STEPS \
    --save_total_limit 1 \
    --learning_rate 5e-4 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --tf32 True \
    --model_max_length $MODEL_MAX_LENGTH \
    --gradient_checkpointing True \
    --dataloader_num_workers $DATALOADER_WORKERS \
    --lazy_preprocess True \
    --report_to wandb \
    --lora_enable True \
    --lora_r $LORA_R \
    --lora_alpha $LORA_ALPHA \
