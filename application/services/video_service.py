from __future__ import annotations

from dataclasses import dataclass

from application.utils.file_helper import require_existing_path
from tools.web_tools import extract_frames


@dataclass
class VideoService:
    def extract_frames(self, source: str, output_dir: str, interval: int = 30, output_format: str = "jpg"):
        return extract_frames(
            video_path=str(require_existing_path(source, "视频文件路径")),
            output_dir=output_dir,
            interval=interval,
        )
