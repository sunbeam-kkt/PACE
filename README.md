# PACE: Privileged Assistance for Counterfactual Execution in Assistant-Free UAV Vision-Language Navigation

<p align="center">
  <a href="YOUR_PAPER_LINK"><img src="https://img.shields.io/badge/Paper-arXiv-red"></a>
  <a href="YOUR_PROJECT_PAGE_LINK"><img src="https://img.shields.io/badge/Project-Page-blue"></a>
  <a href="YOUR_DATASET_LINK"><img src="https://img.shields.io/badge/Dataset-Download-green"></a>
  <a href="YOUR_LICENSE_LINK"><img src="https://img.shields.io/badge/License-MIT-yellow"></a>
</p>

<p align="center">
  <b>Assistant-free UAV vision-language navigation with internalized privileged assistance, counterfactual route validation, and physically executable planning.</b>
</p>

---

## 📌 Overview

This repository provides the official implementation of **PACE**, a privileged-assistance-driven framework for **assistant-free UAV vision-language navigation**.

Existing UAV-VLN agents often rely on external assistance during navigation, such as corrective guidance, route hints, or intervention signals. However, such assistance is usually unavailable during real deployment. PACE addresses this gap by converting privileged runtime support into an internal decision capability that can be used without external help at test time.

PACE contains three key components:

1. **Privileged Assistance Internalization**
   Distills training-only privileged signals into an internal correction state, enabling the agent to recover from route deviation without external assistance.

2. **Counterfactual Route Validation**
   Separates intended routes from plausible but incorrect alternatives, improving long-horizon route discrimination and reducing wrong-target navigation.

3. **Affordance-aware Executable Planning**
   Grounds validated navigation decisions into physically feasible and information-seeking UAV motion.

---

## 🖼️ Framework

<p align="center">
  <img src="[assets/framework.png](https://github.com/sunbeam-kkt/PACE/blob/master/Figure2.png)" width="90%">
</p>

PACE first learns from privileged teacher signals during training. At deployment, the UAV agent no longer receives external assistance. Instead, it uses the learned internal assistance state to support self-correction, counterfactual reasoning, and executable trajectory planning.

---

## 🔥 News

* `[YYYY-MM-DD]` Code and dataset preparation instructions released.
* `[YYYY-MM-DD]` PACE accepted by / submitted to `CONFERENCE_NAME`.
* `[YYYY-MM-DD]` Preprint released.

---

## ✅ TODO

* [ ] Release training code.
* [ ] Release evaluation code.
* [ ] Release pretrained checkpoints.
* [ ] Release dataset preprocessing scripts.
* [ ] Release visualization tools.
* [ ] Release full documentation.

---

## 📂 Repository Structure

```text
PACE/
├── assets/                         # Figures used in README
├── configs/                        # Training and evaluation configs
│   ├── train_pace.yaml
│   └── eval_pace.yaml
├── data/                           # Dataset preparation scripts
│   ├── preprocess.py
│   └── split_dataset.py
├── datasets/                       # Dataset loading modules
├── models/                         # PACE model components
│   ├── privileged_distillation.py
│   ├── counterfactual_validator.py
│   ├── affordance_planner.py
│   └── pace_agent.py
├── trainers/                       # Training pipeline
├── evaluators/                     # Evaluation metrics and benchmark scripts
├── scripts/                        # Running scripts
│   ├── train.sh
│   ├── eval.sh
│   └── visualize.sh
├── tools/                          # Utility functions
├── requirements.txt
└── README.md
```

---

## 🧩 Method

### 1. Privileged Assistance Internalization

During training, the agent has access to privileged assistance signals, such as correction hints, recovery labels, or teacher trajectories. PACE uses these signals only as supervision and distills them into an internal assistance state.

At test time, the agent does not receive any external help. The learned internal state supports recovery-critical decision making.

### 2. Counterfactual Route Validation

UAV navigation in city-scale environments often contains visually similar landmarks and ambiguous route choices. PACE introduces counterfactual validation to compare the intended route with plausible alternatives.

This module encourages the agent to answer not only “where should I go?” but also “why should I not choose another similar route?”

### 3. Affordance-aware Executable Planning

After route validation, PACE grounds the decision into UAV-executable motion. The planner considers local feasibility, collision risk, visibility, and information gain to generate stable short-horizon trajectories.

---

## 📊 Main Results

### Comparison with Existing Methods

| Method     |  NE ↓ |  SR ↑ | SPL ↑ | RSR ↑ | CRA ↑ | CVR ↓ |
| ---------- | ----: | ----: | ----: | ----: | ----: | ----: |
| Baseline-1 |     - |     - |     - |     - |     - |     - |
| Baseline-2 |     - |     - |     - |     - |     - |     - |
| Baseline-3 |     - |     - |     - |     - |     - |     - |
| **PACE**   | **-** | **-** | **-** | **-** | **-** | **-** |

### Ablation Study

| Variant                             |  NE ↓ |  SR ↑ | SPL ↑ | RSR ↑ | CRA ↑ | CVR ↓ |
| ----------------------------------- | ----: | ----: | ----: | ----: | ----: | ----: |
| PACE w/o privileged internalization |     - |     - |     - |     - |     - |     - |
| PACE w/o counterfactual validation  |     - |     - |     - |     - |     - |     - |
| PACE w/o affordance planning        |     - |     - |     - |     - |     - |     - |
| **PACE full**                       | **-** | **-** | **-** | **-** | **-** | **-** |

---

## 🗃️ Dataset

We evaluate PACE on assistant-free UAV vision-language navigation benchmarks.

Please organize the dataset as follows:

```text
DATA_ROOT/
├── train/
│   ├── images/
│   ├── instructions.json
│   ├── trajectories.json
│   └── privileged_signals.json
├── val/
│   ├── images/
│   ├── instructions.json
│   └── trajectories.json
└── test/
    ├── images/
    ├── instructions.json
    └── trajectories.json
```

Set the dataset path in the config file:

```yaml
dataset:
  root: /path/to/DATA_ROOT
  train_split: train
  val_split: val
  test_split: test
```

---

## ⚙️ Installation

### 1. Clone this repository

```bash
git clone https://github.com/YOUR_USERNAME/PACE.git
cd PACE
```

### 2. Create environment

```bash
conda create -n pace python=3.10 -y
conda activate pace
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Optional dependencies for visualization:

```bash
pip install matplotlib opencv-python imageio
```

---

## 🚀 Training

Train PACE with the following command:

```bash
bash scripts/train.sh
```

Or run directly:

```bash
python train.py \
  --config configs/train_pace.yaml \
  --data_root /path/to/DATA_ROOT \
  --output_dir outputs/pace
```

Example training script:

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 python train.py \
  --config configs/train_pace.yaml \
  --batch_size 32 \
  --epochs 20 \
  --lr 5e-5 \
  --output_dir outputs/pace
```

---

## 🔍 Evaluation

Evaluate a trained checkpoint:

```bash
bash scripts/eval.sh
```

Or run directly:

```bash
python eval.py \
  --config configs/eval_pace.yaml \
  --checkpoint outputs/pace/checkpoints/best.pth \
  --data_root /path/to/DATA_ROOT \
  --split test
```

The evaluation script reports:

* `NE`: Navigation Error
* `SR`: Success Rate
* `SPL`: Success weighted by Path Length
* `RSR`: Recovery Success Rate
* `CRA`: Counterfactual Route Accuracy
* `CVR`: Collision Violation Rate

---

## 📈 Visualization

Visualize navigation trajectories, recovery behavior, and counterfactual route validation:

```bash
python visualize.py \
  --checkpoint outputs/pace/checkpoints/best.pth \
  --data_root /path/to/DATA_ROOT \
  --save_dir outputs/visualization
```

Expected outputs:

```text
outputs/visualization/
├── trajectory_vis/
├── counterfactual_routes/
├── recovery_cases/
└── failure_cases/
```

---

## 🧪 Pretrained Models

Pretrained checkpoints will be released at:

| Model      | Dataset       | Link        |
| ---------- | ------------- | ----------- |
| PACE-base  | UAV-Need-Help | Coming soon |
| PACE-large | UAV-Need-Help | Coming soon |

After downloading, place checkpoints under:

```text
checkpoints/
└── pace_best.pth
```

---

## 📌 Reproducibility

To reproduce the main results in the paper:

```bash
bash scripts/reproduce_main_results.sh
```

To reproduce the ablation study:

```bash
bash scripts/reproduce_ablation.sh
```

To reproduce visualization figures:

```bash
bash scripts/reproduce_figures.sh
```

---

## 📝 Citation

If you find this repository useful, please consider citing our paper:

```bibtex
@inproceedings{your2027pace,
  title={PACE: Privileged Assistance for Counterfactual Execution in Assistant-Free UAV Vision-Language Navigation},
  author={Author One and Author Two and Author Three},
  booktitle={Proceedings of the AAAI Conference on Artificial Intelligence},
  year={2027}
}
```

---

## 🙏 Acknowledgements

This project builds upon prior research in vision-language navigation, UAV navigation, privileged learning, counterfactual reasoning, and embodied decision making.

We thank the authors of related UAV-VLN benchmarks and open-source navigation frameworks for their valuable contributions to the community.

---

## 📄 License

This project is released under the `MIT License`. Please see `LICENSE` for more details.

---

## 📬 Contact

For questions, please contact:

```text
YOUR_NAME: your_email@example.com
```

or open an issue in this repository.
