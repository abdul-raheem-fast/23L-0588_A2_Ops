# VisionGuard

[![CI](https://github.com/abdul-raheem-fast/23L-0588_A2_Ops/actions/workflows/ci.yml/badge.svg)](https://github.com/abdul-raheem-fast/23L-0588_A2_Ops/actions/workflows/ci.yml)

VisionGuard is an image-classification service that estimates whether an uploaded image is real or AI-generated. The project covers dataset auditing, reproducible splits, TensorFlow/Keras training, MLflow experiment tracking, Flask inference, request history, Docker Compose, and external model serving.

## Links

- [GitHub repository](https://github.com/abdul-raheem-fast/23L-0588_A2_Ops)
- [DagsHub repository and MLflow](https://dagshub.com/abdul-raheem-fast/23L-0588_A2_Ops)
- [Hugging Face inference Space](https://huggingface.co/spaces/ghaurixd/visionguard-inference)
- [Live Blitz deployment](https://23l-0588-a2-ops.ghauri.prod.page)

## Architecture

```text
Kaggle dataset
      |
      v
Audit and reproducible splits
      |
      v
TensorFlow/Keras training in Colab
      |
      +--> MLflow runs and artifacts on DagsHub
      |
      v
champion.keras
      |
      v
Flask application or Hugging Face Docker inference service
      |
      v
Prediction history database
```

The trained run used a Colab T4 GPU and TensorFlow 2.21.0. TensorFlow 2.18.0 was unavailable in that runtime, so the project records and pins the version actually used.

## Repository layout

| Path | Purpose |
| --- | --- |
| `app/` | Flask application, inference module, configuration, and database layer |
| `scripts/audit_dataset.py` | Image metadata, SHA-256, corruption, and duplicate audit |
| `scripts/make_splits.py` | Seeded class-stratified train/validation/test splits |
| `scripts/train.py` | Baseline CNN, MobileNetV2 transfer learning, fine-tuning, and MLflow logging |
| `notebooks/` | Colab workflow for dataset download, training, and DagsHub tracking |
| `inference-service/` | Docker service for Hugging Face Spaces |
| `configs/` | Training configuration |
| `reports/` | Report source and selected evidence |
| `docker-compose.yml` | Local web/database stack |

## Local setup

Use Python 3.12.

```powershell
cd "D:\MLOps Assignment 2\visionguard"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks environment activation:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

The dataset is expected at `data/raw/` with `AiArtData/` and `RealArt/` subdirectories.

## Audit and split generation

```powershell
python scripts\audit_dataset.py `
  --dataset-dir data\raw `
  --output-dir artifacts\audit

python scripts\make_splits.py `
  --dataset-dir data\raw `
  --output-dir artifacts\splits
```

The audit records dimensions, file size, colour mode, format, SHA-256, unreadable files, and exact duplicates.

## Training

Training is reproducible through a fixed seed, checkpointing, early stopping, and learning-rate reduction:

```powershell
python scripts\train.py --config configs\visionguard.json
```

The completed Colab run produced:

- `baseline_cnn.keras`
- `mobilenetv2_head.keras`
- `mobilenetv2_finetuned.keras`

The selected fine-tuned model is stored locally as `models/champion.keras` and is used by the inference service.

## Colab workflow

Open [the Colab notebook](notebooks/visionguard_colab_training.ipynb) from GitHub. Add `DAGSHUB_USER` and `DAGSHUB_TOKEN` as Colab Secrets, then run the cells in order. The notebook downloads the official Kaggle dataset with `kagglehub`, creates the audit and splits, configures MLflow, trains the models, and downloads the resulting artifacts.

Never place tokens in notebook cells, source files, screenshots, or commits.

For the remaining evaluation evidence, open [the evidence notebook](notebooks/VisionGuard_Evidence_Colab.ipynb) in Colab and run every cell. It downloads the official dataset, loads the public champion model, creates the confusion matrix, ROC curve, error-analysis CSV/grid, and runs eight Keras Tuner trials. Download `visionguard-evidence.zip` from the final cell and place its figures in `reports/figures/`.

## Run the Flask application

The production image installs only the serving dependencies from `requirements.txt`. Training, evaluation, and CI tools are listed separately in `requirements-training.txt`.

```powershell
python -m app
```

Open `http://127.0.0.1:8000`. The application provides:

- Image upload and prediction
- Extension, size, and decode validation
- Honest confidence caveat
- `/health` status endpoint
- `/history` request history

Run the focused tests:

```powershell
python -m pytest tests\test_web.py -q
```

## Docker Compose

Create an untracked `.env` with `POSTGRES_PASSWORD` and `FLASK_SECRET_KEY`, then run:

```powershell
docker compose up --build
```

The web service is published on port `8000`. PostgreSQL is available only inside the Compose network and uses a named volume.

## Deployment

The full Flask application is deployed on Blitz Cloud from the GitHub `main` branch:

```text
https://23l-0588-a2-ops.ghauri.prod.page
```

The service exposes `/health`, `/predict`, and `/history`. The free plan may sleep after inactivity. Training and MLflow dependencies are kept in `requirements-training.txt`; the production image installs only the serving dependencies.

The separate Hugging Face Space remains available as an inference-service deployment attempt, but its free CPU runtime is paused by account quota.

## Hugging Face inference service

The Docker Space uses:

```text
inference-service/
├── Dockerfile
├── app.py
├── requirements.txt
└── models/champion.keras
```

The service listens on port `7860`. After the Space builds, verify it:

```powershell
curl.exe https://ghaurixd-visionguard-inference.hf.space/health
curl.exe -X POST `
  -F "image=@path\to\image.jpg" `
  https://ghaurixd-visionguard-inference.hf.space/predict
```

## Data and secret handling

Raw images, model binaries, ZIP archives, `.env`, tokens, and generated local databases are excluded by `.gitignore`. DagsHub stores experiment metadata and model artifacts; it is not called by the serving application for every prediction.

## Report

The report source is [reports/report.md](reports/report.md). The final PDF is [reports/23L-0588_VisionGuard.pdf](reports/23L-0588_VisionGuard.pdf), and the retained evidence screenshots are indexed in [reports/screenshots/evidence-index.json](reports/screenshots/evidence-index.json).
