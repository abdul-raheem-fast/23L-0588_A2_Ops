import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image, UnidentifiedImageError


def _median(values):
    values = sorted(values)
    if not values:
        return None
    middle = len(values) // 2
    if len(values) % 2:
        return values[middle]
    return (values[middle - 1] + values[middle]) / 2


def audit(dataset_dir):
    rows = []
    for path in sorted(Path(dataset_dir).rglob("*")):
        if not path.is_file():
            continue
        record = {"path": str(path), "class": path.parent.name, "file_size": path.stat().st_size}
        record["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        try:
            with Image.open(path) as image:
                record.update(
                    width=image.width,
                    height=image.height,
                    colour_mode=image.mode,
                    format=image.format,
                    readable=True,
                )
        except (UnidentifiedImageError, OSError):
            record.update(width=None, height=None, colour_mode=None, format=None, readable=False)
        rows.append(record)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", required=True)
    parser.add_argument("--output-dir", default="artifacts/audit")
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = audit(args.dataset_dir)
    with (output_dir / "image_audit.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys() if rows else [])
        writer.writeheader()
        writer.writerows(rows)
    classes = Counter(row["class"] for row in rows)
    hashes = Counter(row["sha256"] for row in rows)
    summary = {
        "images": len(rows),
        "classes": dict(classes),
        "corrupt_files": sum(not row["readable"] for row in rows),
        "exact_duplicate_files": sum(count for count in hashes.values() if count > 1),
        "dimensions": {
            column: {
                "min": min((row[column] for row in rows if row[column] is not None), default=None),
                "median": _median(row[column] for row in rows if row[column] is not None),
                "max": max((row[column] for row in rows if row[column] is not None), default=None),
            }
            for column in ("width", "height", "file_size")
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
