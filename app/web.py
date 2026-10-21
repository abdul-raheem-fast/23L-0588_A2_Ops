import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from .config import Settings
from .db import HistoryStore
from .inference import ImageInference


def create_app(inference=None, store=None):
    settings = Settings()
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "local-development-key")
    app.config["MAX_CONTENT_LENGTH"] = settings.max_content_length
    store = store or HistoryStore(settings.database_url)
    model_error = None
    if inference is None:
        try:
            inference = ImageInference(settings.model_path, settings.threshold)
        except (OSError, ValueError, ImportError) as error:
            model_error = str(error)

    @app.get("/")
    def index():
        return render_template("index.html", model_error=model_error)

    @app.post("/predict")
    def predict():
        upload = request.files.get("image")
        if upload is None or not upload.filename:
            flash("Select an image before submitting.", "error")
            return redirect(url_for("index"))
        filename = secure_filename(upload.filename)
        extension = Path(filename).suffix.lower().removeprefix(".")
        if extension not in settings.allowed_extensions:
            flash("Use a JPG, JPEG, PNG, or WEBP image.", "error")
            return redirect(url_for("index"))
        image_bytes = upload.read()
        if not image_bytes:
            flash("The uploaded file is empty.", "error")
            return redirect(url_for("index"))
        if inference is None:
            flash("The model is not available. Check MODEL_PATH and the application logs.", "error")
            return redirect(url_for("index"))
        try:
            label, confidence = inference.predict(image_bytes)
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("index"))
        store.add_prediction(
            filename,
            label,
            confidence,
            settings.model_name,
            settings.model_version,
        )
        return render_template(
            "result.html",
            filename=filename,
            label=label,
            confidence=f"{confidence:.1%}",
        )

    @app.get("/history")
    def history():
        return render_template("history.html", predictions=store.recent())

    @app.get("/health")
    def health():
        status = "ok" if inference is not None else "degraded"
        return {"status": status, "model": settings.model_name, "version": settings.model_version}, 200

    @app.errorhandler(413)
    def too_large(_error):
        flash("The image is larger than the 10 MB limit.", "error")
        return redirect(url_for("index"))

    return app

