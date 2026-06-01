from __future__ import annotations

import random
import shutil
from collections import defaultdict
from pathlib import Path

import cv2
import xml.etree.ElementTree as ET

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def _ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"路径不存在：{p}")
    return p


def _iter_image_files(images_dir: Path):
    return [p for p in images_dir.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]


def _iter_label_files(labels_dir: Path):
    return [p for p in labels_dir.rglob("*.txt") if p.is_file()]


def _pair_by_stem(images_dir: Path, labels_dir: Path):
    images = _iter_image_files(images_dir)
    labels = _iter_label_files(labels_dir)
    image_map = {p.stem: p for p in images}
    label_map = {p.stem: p for p in labels}
    common = sorted(set(image_map) & set(label_map))
    missing_labels = sorted(set(image_map) - set(label_map))
    missing_images = sorted(set(label_map) - set(image_map))
    pairs = [(image_map[stem], label_map[stem], stem) for stem in common]
    return pairs, missing_labels, missing_images, images, labels


def _debug_file_counts(images_dir: Path, labels_dir: Path):
    pairs, missing_labels, missing_images, images, labels = _pair_by_stem(images_dir, labels_dir)
    return {
        "images_count": len(images),
        "labels_count": len(labels),
        "paired_count": len(pairs),
        "missing_labels": missing_labels[:50],
        "missing_images": missing_images[:50],
        "images_dir": str(images_dir),
        "labels_dir": str(labels_dir),
    }


def count_yolo_classes(labels_dir: str):
    labels_dir = _ensure_dir(labels_dir)
    class_count = defaultdict(int)
    total_boxes = 0
    empty_files = []
    files = _iter_label_files(labels_dir)
    if not files:
        raise ValueError("未找到任何 txt 标注文件")
    for txt_path in files:
        lines = [line.strip() for line in txt_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not lines:
            empty_files.append(str(txt_path))
            continue
        for line in lines:
            class_count[line.split()[0]] += 1
            total_boxes += 1
    return {"total_boxes": total_boxes, "empty_files": empty_files, "class_count": dict(sorted(class_count.items(), key=lambda x: int(x[0])))}


def cleanup_yolo_dataset(images_dir: str, labels_dir: str, dry_run: bool = True):
    images_dir = _ensure_dir(images_dir)
    labels_dir = _ensure_dir(labels_dir)
    deleted_images = []
    deleted_labels = []
    pairs, missing_labels, missing_images, images, labels = _pair_by_stem(images_dir, labels_dir)

    for stem in missing_labels:
        for img in images:
            if img.stem == stem:
                deleted_images.append(str(img))
                if not dry_run:
                    img.unlink()
    for stem in missing_images:
        for lbl in labels:
            if lbl.stem == stem:
                deleted_labels.append(str(lbl))
                if not dry_run:
                    lbl.unlink()

    return {
        "dry_run": dry_run,
        "deleted_images": deleted_images,
        "deleted_labels": deleted_labels,
        "debug": _debug_file_counts(images_dir, labels_dir),
    }


def split_yolo_dataset(data_root: str, train_ratio: float = 0.8, random_seed: int = 42):
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio 必须在 0 和 1 之间")
    random.seed(random_seed)
    root = _ensure_dir(data_root)
    images_dir = root / "images"
    labels_dir = root / "labels"
    if not images_dir.exists() or not labels_dir.exists():
        raise FileNotFoundError("未找到 images 或 labels 文件夹")
    pairs, missing_labels, missing_images, images, labels = _pair_by_stem(images_dir, labels_dir)
    if not pairs:
        raise ValueError(f"没有找到有效的图片-标签对 | 缺失labels={missing_labels[:20]} | 缺失images={missing_images[:20]}")
    random.shuffle(pairs)
    cut = int(len(pairs) * train_ratio)
    train, val = pairs[:cut], pairs[cut:]
    for split in ("train", "val"):
        (images_dir / split).mkdir(parents=True, exist_ok=True)
        (labels_dir / split).mkdir(parents=True, exist_ok=True)

    def mv(items, split):
        for img, lbl, _ in items:
            shutil.move(str(img), str(images_dir / split / img.name))
            shutil.move(str(lbl), str(labels_dir / split / lbl.name))

    mv(train, "train")
    mv(val, "val")
    return {"total": len(pairs), "train": len(train), "val": len(val), "data_root": str(root), "debug": {"missing_labels": missing_labels[:50], "missing_images": missing_images[:50]}}


def generate_blank_labels(images_dir: str, labels_dir: str, overwrite: bool = False):
    images_dir = _ensure_dir(images_dir)
    labels_dir = Path(labels_dir)
    labels_dir.mkdir(parents=True, exist_ok=True)
    created = []
    skipped = []
    for img in _iter_image_files(images_dir):
        rel = img.relative_to(images_dir)
        label = labels_dir / rel.with_suffix(".txt")
        label.parent.mkdir(parents=True, exist_ok=True)
        if label.exists() and not overwrite:
            skipped.append(str(label))
            continue
        label.write_text("", encoding="utf-8")
        created.append(str(label))
    return {"created": created, "skipped": skipped}


def rename_image_label_pairs(images_dir: str, labels_dir: str, prefix="frame_by", start=1, digit=6, dry_run=True):
    images_dir = _ensure_dir(images_dir)
    labels_dir = _ensure_dir(labels_dir)
    pairs, missing_labels, missing_images, images, labels = _pair_by_stem(images_dir, labels_dir)
    debug = {
        "images_dir": str(images_dir),
        "labels_dir": str(labels_dir),
        "images_count": len(images),
        "labels_count": len(labels),
        "paired_count": len(pairs),
        "missing_labels": missing_labels[:50],
        "missing_images": missing_images[:50],
        "image_files": [p.name for p in images],
        "label_files": [p.name for p in labels],
    }
    if missing_labels or missing_images:
        raise ValueError(
            f"图片和标注文件未按 stem 成功配对 | 缺失图片对应标注: {missing_labels[:20]} | 缺失标注对应图片: {missing_images[:20]} | 调试信息: {debug}"
        )
    changes = []
    for idx, (img, txt, _) in enumerate(pairs, start=start):
        new_name = f"{prefix}_{str(idx).zfill(digit)}"
        changes.append({"from": [img.name, txt.name], "to": [f"{new_name}.png", f"{new_name}.txt"]})
        if not dry_run:
            img.rename(images_dir / f"{new_name}.png")
            txt.rename(labels_dir / f"{new_name}.txt")
    return {"dry_run": dry_run, "changes": changes, "debug": debug}


def voc_to_yolo_batch(xml_folder: str, output_folder=None, class_mapping=None):
    xml_folder = _ensure_dir(xml_folder)
    xml_files = list(Path(xml_folder).glob("*.xml"))
    if not xml_files:
        raise ValueError("未找到 XML 文件")
    if class_mapping is None:
        names = sorted({obj.find("name").text for x in xml_files for obj in ET.parse(x).getroot().findall("object") if obj.find("name") is not None})
        class_mapping = {name: i for i, name in enumerate(names)}
    out_dir = Path(output_folder) if output_folder else Path(xml_folder)
    out_dir.mkdir(parents=True, exist_ok=True)
    converted = []
    for xml_path in xml_files:
        root = ET.parse(xml_path).getroot()
        size = root.find("size")
        if size is None:
            continue
        w, h = int(size.find("width").text), int(size.find("height").text)
        lines = []
        for obj in root.findall("object"):
            name = obj.find("name").text
            if name not in class_mapping:
                continue
            box = obj.find("bndbox")
            xmin = float(box.find("xmin").text)
            ymin = float(box.find("ymin").text)
            xmax = float(box.find("xmax").text)
            ymax = float(box.find("ymax").text)
            x = (xmin + xmax) / 2 / w
            y = (ymin + ymax) / 2 / h
            bw = (xmax - xmin) / w
            bh = (ymax - ymin) / h
            lines.append(f"{class_mapping[name]} {x:.6f} {y:.6f} {bw:.6f} {bh:.6f}")
        if lines:
            txt = out_dir / f"{xml_path.stem}.txt"
            txt.write_text("\n".join(lines), encoding="utf-8")
            converted.append(str(txt))
    (out_dir / "classes.txt").write_text("\n".join(class_mapping.keys()), encoding="utf-8")
    return {"converted": converted, "class_mapping": class_mapping, "output_folder": str(out_dir)}


def change_ids_in_labels(labels_dir: str, mapping: dict[int, int]):
    labels_dir = _ensure_dir(labels_dir)
    updated = []
    for txt in labels_dir.rglob("*.txt"):
        lines = []
        for raw in txt.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            parts = raw.split()
            if len(parts) < 5:
                continue
            old = int(parts[0])
            parts[0] = str(mapping.get(old, old))
            lines.append(" ".join(parts))
        txt.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        updated.append(str(txt))
    return {"updated_files": updated}


def extract_frames(video_path: str, output_dir: str, mode="frame", interval=30, quality=95, width=None, height=None, prefix="frame", delete_source=False):
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError("视频文件不存在")
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError("无法打开视频文件")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_interval = int(interval if mode == "frame" else max(1, round(fps * float(interval))))
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    saved = []
    i = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if i % frame_interval == 0:
            if width and height:
                frame = cv2.resize(frame, (int(width), int(height)))
            name = out / f"{prefix}_{len(saved)+1:06d}.jpg"
            cv2.imwrite(str(name), frame, [cv2.IMWRITE_JPEG_QUALITY, int(quality)])
            saved.append(str(name))
        i += 1
    cap.release()
    if delete_source:
        video_path.unlink()
    return {"saved": saved, "output_dir": str(out)}


def record_rtsp_stream(rtsp_url: str, output_dir: str, segment_minutes=5, total_duration=None, prefix="recording"):
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    return {"rtsp_url": rtsp_url, "output_dir": str(out_dir), "segment_minutes": segment_minutes, "total_duration": total_duration, "prefix": prefix, "status": "recording_endpoint_ready"}


def polygon_from_points(image_width: int, image_height: int, points, output_path="polygon_coords.txt"):
    if image_width <= 0 or image_height <= 0:
        raise ValueError("图片宽高必须大于 0")
    if not isinstance(points, list) or len(points) < 3:
        raise ValueError("至少需要 3 个点")
    norm = [[round(x / image_width, 4), round(y / image_height, 4)] for x, y in points]
    Path(output_path).write_text(str([norm]), encoding="utf-8")
    return {"normalized_points": [norm], "output_path": str(Path(output_path).resolve())}
