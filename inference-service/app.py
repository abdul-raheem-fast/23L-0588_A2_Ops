import io
import os

import numpy as np
import tensorflow as tf
from flask import Flask, jsonify, request
from PIL import Image, UnidentifiedImageError

app = Flask(__name__)
model_path = os.getenv("MODEL_PATH", "models/champion.keras")
threshold = float(os.getenv("DECISION_THRESHOLD", "0.5"))
model_name = os.getenv("MODEL_NAME", "visionguard-champion")
model = tf.keras.models.load_model(model_path)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "model": model_name})


@app.post("/predict")
def predict():
    upload = request.files.get("image")
    if upload is None:
        return jsonify({"error": "image field is required"}), 400
    try:
        image = Image.open(io.BytesIO(upload.read())).convert("RGB")
    except (UnidentifiedImageError, OSError):
        return jsonify({"error": "uploaded file is not a readable image"}), 400
    image = image.resize((224, 224))
    batch = np.asarray(image, dtype=np.float32)[None, ...] / 255.0
    probability = float(model.predict(batch, verbose=0).reshape(-1)[0])
    label = "AI-generated" if probability >= threshold else "Real"
    confidence = probability if label == "AI-generated" else 1.0 - probability
    return jsonify({"label": label, "confidence": round(confidence, 4), "model": model_name})

