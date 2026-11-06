# 23L-0588 — VisionGuard

**Student:** Muhammad Abdul Raheem  
**Project:** `23L-0588_A2_Ops`  
**GitHub:** https://github.com/abdul-raheem-fast/23L-0588_A2_Ops  
**DagsHub:** https://dagshub.com/abdul-raheem-fast/23L-0588_A2_Ops  
**Live URL:** https://23l-0588-a2-ops.ghauri.prod.page
**Graded commit:** `2f93a1e`

## Disclosure

An AI assistant was used to help structure the implementation, identify reproducibility requirements, and review wording. All commands, runs, screenshots, account actions, metrics, and interpretations in this report must be produced and verified by the student.

## 1. Data understanding and versioning

### 1.1 Environment

Record the Python, TensorFlow, Keras, Pillow, MLflow, and Docker versions. Include the terminal screenshot showing the environment and GPU check.

The Colab runtime selected a T4 GPU. TensorFlow 2.18.0 was unavailable for that runtime, so the run used TensorFlow 2.21.0; this version change is recorded rather than hidden.

### 1.2 Dataset audit

The audit script records class, file size, dimensions, colour mode, format, SHA-256, readability, and duplicate hashes. Include `artifacts/audit/image_audit.csv`, the summary table, and the screenshot of the command.

The Colab run audited 975 images: 539 from `AiArtData`, 436 from `RealArt`, no corrupt files, and two exact duplicate files.

### 1.3 Visual EDA

Insert the sample grid and class-separated width, height, and file-size histograms. Explain the visible differences and limitations in two or three sentences per figure.

### 1.4 DVC

Document the toy CSV history, pointer contents, remote push/pull, and the dataset-folder application. Include actual commit and terminal screenshots.

## 2. Model development

Explain the `tf.data` pipeline, aspect-ratio decision, baseline CNN, MobileNetV2 head training, last-block fine-tuning, callbacks, threshold selection, evaluation metrics, ROC/confusion matrix, misclassifications, and Keras Tuner results. Insert the generated figures with captions.

## 3. MLflow and DagsHub

Define experiment, run, parameter, metric, artifact, and tag in your own words. Include local toy runs, DagsHub tracking evidence, manual and autologging runs, artifacts, six-run comparison, and two model versions with the `champion` alias.

## 4. Flask application

The model is loaded once during application startup. Upload validation checks the extension, size, and decoded image without persisting the upload. The result shows the label, confidence, and caveat; `/history` reads the request trail and `/health` reports service state.

## 5. Database trail

Each successful prediction stores UTC time, sanitized filename, decision, confidence, model name, and model version. Include the schema and history-page screenshot.

## 6. Docker and Compose

Explain dependency-layer caching, the slim CPU image, non-root execution, health checks, named volumes, service readiness, secret handling, image-size optimization, operations commands, and the intentional failure/fix. Include Docker warm-up and CI evidence.

## 7. API deployment

The application was deployed from the GitHub `main` branch on Blitz Cloud using the repository Dockerfile. The deployment uses the public address `https://23l-0588-a2-ops.ghauri.prod.page`. The build initially failed because the training manifest combined TensorFlow 2.21.0 with MLflow 2.19.0, which require incompatible protobuf ranges. The production and training dependencies were separated, the updated image built successfully, and the public `/health` endpoint returned the deployed model name, version, and `ok` status. The free service may sleep when idle; no paid cloud credits were used.

## 8. Flask and hosted API integration

The deployed Flask service accepts image uploads at `/predict`, renders the prediction result, and records successful requests for `/history`. A real dataset image was sent to the public endpoint and returned an `AI-generated` decision with 71.3% confidence. The health endpoint was also checked independently from outside the local workspace. The service uses SQLite for the free deployment because no managed database was provisioned; production deployments should use PostgreSQL and a secret-managed configuration.

## Submission checklist

- [ ] PDF renamed to `23L-0588_VisionGuard.pdf`
- [x] GitHub repository link
- [x] DagsHub project link
- [x] Live API URL tested from another network
- [ ] Every evidence item is a real, captioned screenshot
- [x] No credentials appear in source, screenshots, or report
