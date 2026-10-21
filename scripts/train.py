import argparse
import json
import os
import random
from pathlib import Path

import mlflow
import mlflow.tensorflow
import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score


def to_binary_labels(labels):
    return np.asarray(
        [1.0 if str(label).strip().lower() in {"aiartdata", "ai-generated", "ai_generated"} else 0.0 for label in labels],
        dtype="float32",
    )


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def dataset_from_csv(csv_path, image_size, batch_size, training):
    import pandas as pd

    frame = pd.read_csv(csv_path)
    labels = to_binary_labels(frame["label"])
    paths = frame["path"].to_numpy()
    dataset = tf.data.Dataset.from_tensor_slices((paths, labels))

    def load(path, label):
        image = tf.io.read_file(path)
        image = tf.io.decode_image(image, channels=3, expand_animations=False)
        image.set_shape([None, None, 3])
        image = tf.image.resize(image, [image_size, image_size])
        image = tf.cast(image, tf.float32) / 255.0
        return image, label

    dataset = dataset.map(load, num_parallel_calls=tf.data.AUTOTUNE)
    if training:
        dataset = dataset.shuffle(len(paths), seed=23, reshuffle_each_iteration=True)
    return dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)


def baseline_model(image_size):
    inputs = tf.keras.Input((image_size, image_size, 3))
    x = tf.keras.layers.Conv2D(32, 3, padding="same", activation="relu")(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling2D()(x)
    x = tf.keras.layers.Conv2D(64, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling2D()(x)
    x = tf.keras.layers.Conv2D(128, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.35)(x)
    return tf.keras.Model(inputs, tf.keras.layers.Dense(1, activation="sigmoid")(x), name="baseline_cnn")


def transfer_model(image_size, learning_rate):
    inputs = tf.keras.Input((image_size, image_size, 3))
    base = tf.keras.applications.MobileNetV2(
        input_shape=(image_size, image_size, 3), include_top=False, weights="imagenet"
    )
    base.trainable = False
    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs * 255.0)
    x = base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    model = tf.keras.Model(inputs, tf.keras.layers.Dense(1, activation="sigmoid")(x), name="mobilenetv2")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.Precision(), tf.keras.metrics.Recall()],
    )
    return model, base


def compile_model(model, learning_rate):
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.Precision(), tf.keras.metrics.Recall()],
    )


def evaluate(model, dataset, labels):
    probabilities = model.predict(dataset, verbose=0).reshape(-1)
    return {
        "accuracy": accuracy_score(labels, probabilities >= 0.5),
        "precision": precision_score(labels, probabilities >= 0.5, zero_division=0),
        "recall": recall_score(labels, probabilities >= 0.5, zero_division=0),
        "f1": f1_score(labels, probabilities >= 0.5, zero_division=0),
        "roc_auc": roc_auc_score(labels, probabilities),
    }


def train_one(name, model, train, validation, test, test_labels, config, model_dir):
    compile_model(model, config["learning_rate"])
    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.25, patience=2),
        tf.keras.callbacks.ModelCheckpoint(model_dir / f"{name}.keras", monitor="val_loss", save_best_only=True),
    ]
    with mlflow.start_run(run_name=name):
        mlflow.log_params({**config, "model": name})
        history = model.fit(train, validation_data=validation, epochs=config["epochs"], callbacks=callbacks)
        metrics = evaluate(model, test, test_labels)
        mlflow.log_metrics(metrics)
        mlflow.tensorflow.log_model(model, name="model")
        print(json.dumps({"model": name, "best_epoch": int(np.argmin(history.history["val_loss"]) + 1), **metrics}, indent=2))
    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    set_seed(config["seed"])
    data_dir = Path(config["data_dir"])
    model_dir = Path(config["model_dir"])
    model_dir.mkdir(parents=True, exist_ok=True)
    train = dataset_from_csv(data_dir / "train.csv", config["image_size"], config["batch_size"], True)
    validation = dataset_from_csv(data_dir / "validation.csv", config["image_size"], config["batch_size"], False)
    test = dataset_from_csv(data_dir / "test.csv", config["image_size"], config["batch_size"], False)
    import pandas as pd

    test_labels = to_binary_labels(pd.read_csv(data_dir / "test.csv")["label"]).astype("int32")
    mlflow.set_experiment(config["mlflow_experiment"])
    if os.getenv("MLFLOW_TRACKING_URI"):
        mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    train_one("baseline_cnn", baseline_model(config["image_size"]), train, validation, test, test_labels, config, model_dir)
    transfer, base = transfer_model(config["image_size"], config["learning_rate"])
    train_one("mobilenetv2_head", transfer, train, validation, test, test_labels, config, model_dir)
    base.trainable = True
    for layer in base.layers[:-20]:
        layer.trainable = False
    transfer.compile(optimizer=tf.keras.optimizers.Adam(config["learning_rate"] / 10), loss="binary_crossentropy", metrics=["accuracy"])
    train_one("mobilenetv2_finetuned", transfer, train, validation, test, test_labels, config, model_dir)


if __name__ == "__main__":
    main()
