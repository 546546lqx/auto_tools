from __future__ import annotations

from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    TOOLS_DIR = BASE_DIR / "tools"
    STATE_DIR = BASE_DIR / ".state"
    RTSP_JOBS_FILE = STATE_DIR / "rtsp_jobs.json"
    DEBUG = False
    JSON_AS_ASCII = False
    DEFAULT_OUTPUT_DIR = str(BASE_DIR)
    DEFAULT_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"]


class DevelopmentConfig(Config):
    DEBUG = True
