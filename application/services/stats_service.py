from __future__ import annotations

from dataclasses import dataclass

from application.utils.file_helper import require_existing_path
from tools.web_tools import cleanup_yolo_dataset, count_yolo_matched_pairs


@dataclass
class StatsService:
    def count_classes(self, labels_dir: str, images_dir: str):
        labels_path = str(require_existing_path(labels_dir, "标注文件夹路径"))
        images_path = str(require_existing_path(images_dir, "图片文件夹路径"))
        return count_yolo_matched_pairs(images_path, labels_path)

    def cleanup_dataset(self, images_dir: str, labels_dir: str, dry_run: bool = True):
        images_path = str(require_existing_path(images_dir, "图片文件夹路径"))
        labels_path = str(require_existing_path(labels_dir, "标注文件夹路径"))
        result = cleanup_yolo_dataset(images_path, labels_path, dry_run=dry_run)
        result["images_dir"] = images_path
        result["labels_dir"] = labels_path
        return result
