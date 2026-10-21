import argparse
import csv
import random
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", required=True)
    parser.add_argument("--output-dir", default="artifacts/splits")
    parser.add_argument("--seed", type=int, default=23)
    args = parser.parse_args()
    paths, labels = [], []
    for path in sorted(Path(args.dataset_dir).rglob("*")):
        if path.is_file():
            paths.append(str(path.resolve()))
            labels.append(path.parent.name)
    random.seed(args.seed)
    grouped = {}
    for path, label in zip(paths, labels):
        grouped.setdefault(label, []).append(path)
    train_paths, train_labels = [], []
    validation_paths, validation_labels = [], []
    test_paths, test_labels = [], []
    for label, class_paths in grouped.items():
        random.shuffle(class_paths)
        test_count = max(1, round(len(class_paths) * 0.1))
        validation_count = max(1, round(len(class_paths) * 0.1))
        test_class = class_paths[:test_count]
        validation_class = class_paths[test_count:test_count + validation_count]
        train_class = class_paths[test_count + validation_count:]
        train_paths.extend(train_class)
        train_labels.extend([label] * len(train_class))
        validation_paths.extend(validation_class)
        validation_labels.extend([label] * len(validation_class))
        test_paths.extend(test_class)
        test_labels.extend([label] * len(test_class))
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for name, split_paths, split_labels in (
        ("train", train_paths, train_labels),
        ("validation", validation_paths, validation_labels),
        ("test", test_paths, test_labels),
    ):
        with (output / f"{name}.csv").open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["path", "label"])
            writer.writerows(zip(split_paths, split_labels))
    print(f"Created reproducible train/validation/test splits in {output}")


if __name__ == "__main__":
    main()
