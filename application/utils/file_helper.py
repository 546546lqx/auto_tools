from __future__ import annotations

from pathlib import Path


def require_existing_path(value: str | None, label: str) -> Path:
    """Validate that a user-provided path exists and return it as Path."""
    text = (value or "").strip()
    if not text:
        raise ValueError(f"请填写 {label}")
    path = Path(text)
    if not path.exists():
        raise FileNotFoundError(f"路径不存在：{path}")
    return path


def require_text(value: str | None, label: str) -> str:
    text = (value or "").strip()
    if not text:
        raise ValueError(f"请填写 {label}")
    return text
