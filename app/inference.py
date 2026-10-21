from io import BytesIO

from PIL import Image, UnidentifiedImageError


class ImageInference:
    image_size = (224, 224)

    def __init__(self, model_path, threshold):
        import tensorflow as tf

        self.model = tf.keras.models.load_model(model_path)
        self.threshold = threshold

    def predict(self, image_bytes):
        import numpy as np

        try:
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
        except (UnidentifiedImageError, OSError) as error:
            raise ValueError("The uploaded file is not a readable image.") from error
        image = image.resize(self.image_size)
        batch = np.asarray(image, dtype=np.float32)[None, ...] / 255.0
        probability = float(np.asarray(self.model.predict(batch, verbose=0)).reshape(-1)[0])
        label = "AI-generated" if probability >= self.threshold else "Real"
        confidence = probability if label == "AI-generated" else 1.0 - probability
        return label, confidence
