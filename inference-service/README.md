---
title: VisionGuard Inference
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# VisionGuard Inference API

This Space serves the trained VisionGuard classifier through Flask.

## Endpoints

- `GET /health`
- `POST /predict` with an image field
