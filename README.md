# VisionGuard

VisionGuard classifies an uploaded image as real or AI-generated. The project contains a reproducible TensorFlow training pipeline, MLflow instrumentation, a Flask application, SQLite request history, and a Docker Compose deployment.

[![CI](https://github.com/23L-0588/23L-0588_A2_Ops/actions/workflows/ci.yml/badge.svg)](https://github.com/23L-0588/23L-0588_A2_Ops/actions/workflows/ci.yml)

Repository links:

- GitHub: https://github.com/abdul-raheem-fast/23L-0588_A2_Ops
- DagsHub: https://dagshub.com/abdul-raheem-fast/23L-0588_A2_Ops

## Project setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `DATASET_DIR` to the extracted Kaggle dataset directory. Run the audit before training:

```powershell
python scripts\audit_dataset.py --dataset-dir $env:DATASET_DIR --output-dir artifacts\audit
python scripts\make_splits.py --dataset-dir $env:DATASET_DIR --output-dir artifacts\splits
python scripts\train.py --config configs\visionguard.json
python -m app
```

The report is built from `reports/report.md` after replacing evidence placeholders with genuine screenshots and run values.

The `inference-service` directory is the Docker service for the Hugging Face Space. Copy only the selected, trained `champion.keras` model into `inference-service/models/` after training; never upload the raw dataset or credentials.

## Hugging Face inference deployment

Upload the contents of `inference-service` to the Docker Space `ghaurixd/visionguard-inference`. The Space must contain `Dockerfile`, `app.py`, `requirements.txt`, and `models/champion.keras`. The container listens on port `7860`.

After the Space finishes building, verify:

```powershell
curl.exe https://ghaurixd-visionguard-inference.hf.space/health
curl.exe -X POST -F "image=@path\to\image.jpg" https://ghaurixd-visionguard-inference.hf.space/predict
```

The model was trained in Colab with TensorFlow 2.21.0 because TensorFlow 2.18.0 was unavailable in that runtime. The same TensorFlow version is pinned in the inference service.

## Environment variables

The application reads its model, threshold, database, and deployment settings from `.env`. Secrets are never stored in source code.
