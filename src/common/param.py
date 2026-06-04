import argparse
import os
import datetime
from pathlib import Path
from utils.CN import CN
import transformers
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CommonArguments:
    project_prefix: str = field(
        default_factory=lambda: str(Path(str(os.getcwd())).parent.resolve()),
        metadata={"help": "project path"}
    )
    run_type: str = field(default="train", metadata={"help": "run_type in [collect, train, eval]"})
    collect_type: str = field(default="dagger", metadata={"help": "collect_type in [dagger]"})
    name: str = field(default='default', metadata={"help": 'experiment name'})

    maxInput: int = field(default=500, metadata={"help": "max input instruction"})
    maxWaypoints: int = field(default=500, metadata={"help": 'max action sequence'})

    dagger_it: int = field(default=1)
    epochs: int = field(default=10)
    lr: float = field(default=0.00025, metadata={"help": "learning rate"})
    batchSize: int = field(default=8)
    trainer_gpu_device: int = field(default=0, metadata={"help": 'GPU'})

    inflection_weight_coef: float = field(default=1.9)

    dagger_mode_load_scene: List[str] = field(default_factory=list)
    dagger_update_size: int = field(default=8000)
    dagger_mode: str = field(default="end", metadata={"help": 'dagger mode in [end middle nearest]'})
    dagger_p: float = field(default=1.0, metadata={"help": 'dagger p'})

    tokenizer_use_bert: bool = field(default=True)

    simulator_tool_port: int = field(default=30000, metadata={"help": "simulator_tool port"})
    DDP_MASTER_PORT: int = field(default=20001, metadata={"help": "DDP MASTER_PORT"})

    continue_start_from_dagger_it: Optional[int] = field(default=None)
    continue_start_from_checkpoint_path: Optional[str] = field(default=None)

    vlnbert: bool = field(default=False)
    featdropout: float = field(default=0.4)
    action_feature: int = field(default=32)
    
    eval_save_path: Optional[str] = field(default=None)
    dagger_save_path: Optional[str] = field(default=None)
    activate_maps: Optional[List[str]] = field(default_factory=list)

    gpu_id: int = field(default=3, metadata={"help": "simulator gpus"})
    always_help: bool = field(default=False)
    use_gt: bool = field(default=False)
    
    fast_mode: bool = field(default=False, metadata={"help": "enable speed-oriented runtime defaults"})
    inference_dtype: str = field(default="bf16", metadata={"help": "runtime dtype in [bf16, fp16, fp32]"})
    use_amp: bool = field(default=True, metadata={"help": "use torch autocast during inference"})
    allow_tf32: bool = field(default=True, metadata={"help": "enable TF32 matmul/cudnn on Ampere+ GPUs"})
    cudnn_benchmark: bool = field(default=True, metadata={"help": "enable cudnn benchmark for fixed image sizes"})
    llm_use_cache: bool = field(default=False, metadata={"help": "forward use_cache flag for the LLM"})
    empty_cache_each_forward: bool = field(default=False, metadata={"help": "call torch.cuda.empty_cache inside multimodal forward"})
    merge_lora_for_inference: bool = field(default=True, metadata={"help": "merge PEFT LoRA weights after loading for faster inference"})
    done_detection_interval: int = field(default=1, metadata={"help": "run GroundingDINO done detection every N steps; <=0 disables it"})
    assist_use_dino: bool = field(default=True, metadata={"help": "use GroundingDINO inside the external assistant"})
    assist_dino_interval: int = field(default=1, metadata={"help": "run assistant GroundingDINO every N assistant calls"})
    assist_dino_cameras: Optional[str] = field(default=None, metadata={"help": "comma-separated assistant DINO camera names; default uses all cameras"})
    dino_device: Optional[str] = field(default=None, metadata={"help": "GroundingDINO device, e.g. cuda:0 or cpu; default follows gpu_id"})
    log_step_interval: int = field(default=1, metadata={"help": "log closed-loop steps every N steps"})
    verbose_runtime: bool = field(default=True, metadata={"help": "print detailed runtime diagnostics"})
    hf_offline: bool = field(default=True, metadata={"help": "force Hugging Face loaders to use local files only"})
    use_internalized_assistant: bool = field(default=False, metadata={"help": "enable latent assistant heads and disable external assistant text when requested"})
    disable_external_assistant: bool = field(default=False, metadata={"help": "do not feed external assistant notice text to the student"})
    selfhelp_dagger: bool = field(default=False, metadata={"help": "collect DAgger with teacher supervision but no online assistant text input"})
    use_counterfactual_grounding: bool = field(default=False, metadata={"help": "enable candidate scoring and counterfactual rejection at inference/training"})
    use_affordance_field: bool = field(default=False, metadata={"help": "enable local aerial affordance field and planner"})
    candidate_count: int = field(default=6, metadata={"help": "number of local counterfactual/planner waypoint candidates"})
    innovation_trace_path: Optional[str] = field(default=None, metadata={"help": "optional JSONL path for dumping real innovation/affordance outputs during eval"})
    innovation_trace_max_records: int = field(default=200, metadata={"help": "maximum number of per-sample innovation trace records to dump; <=0 means unlimited"})
    innovation_trace_stride: int = field(default=1, metadata={"help": "dump one innovation trace every N closed-loop steps"})
    innovation_trace_include_affordance_field: bool = field(default=True, metadata={"help": "include full local affordance field logits in the JSONL trace"})
    help_loss_scale: float = field(default=0.2)
    ranking_loss_scale: float = field(default=0.2)
    rejection_loss_scale: float = field(default=0.1)
    affordance_loss_scale: float = field(default=0.1)
    distillation_loss_scale: float = field(default=0.1)

    dataset_path: Optional[str] = field(default=None)
    eval_json_path: Optional[str] = field(default=None)
    train_json_path: Optional[str] = field(default=None)
    object_name_json_path: Optional[str] = field(default=None)
    map_spawn_area_json_path: Optional[str] = field(default=None)
    
@dataclass
class DataArguments:
    data_path: str = field(default=None,
                           metadata={"help": "Path to the training data."})
    lazy_preprocess: bool = False
    is_multimodal: bool = False
    image_grid_pinpoints: Optional[str] = field(default=None)
    input_prompt: Optional[str] = field(default=None)
    refine_prompt: Optional[bool] = field(default=True)
    mm_use_im_start_end: bool = field(default=False)

    
@dataclass
class ModelArguments:
    model_path: Optional[str] = field(default="facebook/opt-350m")
    model_base: Optional[str] = field(default=None)
    traj_model_path: Optional[str] = field(default=None)
    vision_tower: Optional[str] = field(default=None)
    image_processor: Optional[str] = field(default=None)
    groundingdino_config: Optional[str] = field(default=None)
    groundingdino_model_path: Optional[str] = field(default=None)
    bert_model_path: Optional[str] = field(default=None, metadata={"help": "local bert-base-uncased directory for Q-Former tokenizer/config/weights"})
    
    
parser = transformers.HfArgumentParser((CommonArguments, ModelArguments, DataArguments))
args, model_args, data_args = parser.parse_args_into_dataclasses()

args.make_dir_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
args.logger_file_name = '{}/workdir/{}/logs/{}_{}.log'.format(args.project_prefix, args.run_type, args.collect_type, args.make_dir_time)

if args.hf_offline:
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

if args.fast_mode:
    args.allow_tf32 = True
    args.cudnn_benchmark = True
    args.use_amp = True
    args.merge_lora_for_inference = True
    args.empty_cache_each_forward = False
    args.log_step_interval = max(5, int(args.log_step_interval))
    args.assist_dino_interval = max(3, int(args.assist_dino_interval))


# args.run_type = 'collect'
assert args.run_type in ['collect', 'train', 'eval'], 'run_type error'
# args.collect_type = 'TF'
assert args.collect_type in ['TF', 'dagger'], 'collect_type error'


args.machines_info = [
    {
        'MACHINE_IP': '127.0.0.1',
        'SOCKET_PORT': int(args.simulator_tool_port),
        'MAX_SCENE_NUM': 16,
        'open_scenes': [],
    },
]


args.TRAIN_VOCAB = Path(args.project_prefix) / 'DATA/data/aerialvln/train_vocab.txt'
args.TRAINVAL_VOCAB = Path(args.project_prefix) / 'DATA/data/aerialvln/train_vocab.txt'
args.vocab_size = 10038


default_config = CN.clone()
default_config.make_dir_time = args.make_dir_time
default_config.freeze()
