from __future__ import annotations

from dataclasses import dataclass

from application.utils.file_helper import require_existing_path
from tools.web_tools import cleanup_yolo_dataset, count_yolo_classes


@dataclass
class StatsService:
    def count_classes(self, labels_dir: str, images_dir: str | None = None):
        labels_path = str(require_existing_path(labels_dir, "标注文件夹路径"))
        result = count_yolo_classes(labels_path)
        result["images_dir"] = images_dir or ""
        return result

    def cleanup_dataset(self, images_dir: str, labels_dir: str, dry_run: bool = True):
        images_path = str(require_existing_path(images_dir, "图片文件夹路径"))
        labels_path = str(require_existing_path(labels_dir, "标注文件夹路径"))
        result = cleanup_yolo_dataset(images_path, labels_path, dry_run=dry_run)
        result["images_dir"] = images_path
        result["labels_dir"] = labels_path
        return result
