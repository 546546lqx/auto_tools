from __future__ import annotations

from dataclasses import dataclass

from application.utils.file_helper import require_existing_path
from tools.web_tools import rename_image_label_pairs, split_yolo_dataset


@dataclass
class SplitService:
    def split_dataset(self, data_root: str, train_ratio: float = 0.8, val_ratio: float = 0.2, rename_files: bool = False):
        if not 0 < train_ratio < 1:
            raise ValueError("train_ratio 必须在 0 和 1 之间")
        if not 0 <= val_ratio < 1:
            raise ValueError("val_ratio 必须在 0 和 1 之间")
        if abs((train_ratio + val_ratio) - 1.0) > 1e-6:
            raise ValueError("train / val 比例之和必须等于 1")
        result = split_yolo_dataset(str(require_existing_path(data_root, "数据集根目录")), train_ratio=train_ratio)
        result["val_ratio"] = val_ratio
        result["rename_files"] = rename_files
        return result

    def rename_pairs(self, images_dir: str, labels_dir: str, prefix: str = "frame_by", start: int = 1, digit: int = 6, dry_run: bool = True):
        try:
            return rename_image_label_pairs(
                str(require_existing_path(images_dir, "图片文件夹路径")),
                str(require_existing_path(labels_dir, "标注文件夹路径")),
                prefix=prefix,
                start=start,
                digit=digit,
                dry_run=dry_run,
            )
        except ValueError as exc:
            if "图片数量与标注数量不一致" in str(exc):
                raise ValueError(str(exc)) from exc
            raise
