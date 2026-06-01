from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from application.utils.file_helper import require_existing_path
from tools.web_tools import extract_frames, polygon_from_points, voc_to_yolo_batch


@dataclass
class ConvertService:
    def convert_dataset(self, source_format: str, input_dir: str, output_dir: str | None = None, class_mapping_text: str = ""):
        source_format = (source_format or "VOC").upper()
        input_path = str(require_existing_path(input_dir, "输入目录"))
        class_mapping = None
        if class_mapping_text.strip():
            text = class_mapping_text.strip()
            try:
                class_mapping = json.loads(text)
            except Exception:
                class_mapping = self._parse_mapping_text(text)
        if source_format == "VOC":
            result = voc_to_yolo_batch(input_path, output_folder=output_dir, class_mapping=class_mapping)
            result["source_format"] = source_format
            return result
        raise ValueError(f"暂不支持的格式：{source_format}")

    def extract_frames(self, source: str, output_dir: str, interval: int = 30, output_format: str = "jpg"):
        result = extract_frames(video_path=str(require_existing_path(source, "视频文件或 RTSP 地址")), output_dir=output_dir, interval=interval)
        result["output_format"] = output_format
        return result

    def save_polygon(self, image_width: int, image_height: int, points_text: str, output_path: str):
        points = json.loads(points_text) if points_text.strip() else []
        return polygon_from_points(image_width=image_width, image_height=image_height, points=points, output_path=output_path)

    def _parse_mapping_text(self, text: str) -> dict:
        mapping = {}
        for line in text.splitlines():
            if not line.strip():
                continue
            if "->" in line:
                left, right = line.split("->", 1)
            elif ":" in line:
                left, right = line.split(":", 1)
            else:
                continue
            mapping[left.strip()] = int(right.strip())
        return mapping
