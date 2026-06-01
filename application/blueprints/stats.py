from __future__ import annotations

import json
from flask import Blueprint, render_template, request

from application.services.stats_service import StatsService

bp = Blueprint("stats", __name__)


def _debug_summary(title: str, payload: dict) -> str:
    return f"{title}\n" + json.dumps(payload, ensure_ascii=False, indent=2)


@bp.get("/stats")
def stats_page():
    return render_template("stats.html", result=None, form=request.form)


@bp.post("/stats")
def stats_submit():
    service = StatsService()
    labels_dir = request.form.get("labels_dir", "").strip()
    images_dir = request.form.get("images_dir", "").strip()
    try:
        result = service.count_classes(labels_dir, images_dir or None)
        return render_template("stats.html", result={"success": True, "message": "统计完成", "data": result, "debug": _debug_summary("统计调试信息", result)}, form=request.form)
    except Exception as exc:
        return render_template("stats.html", result={"success": False, "message": str(exc), "data": {}, "debug": f"统计失败\nlabels_dir={labels_dir}\nimages_dir={images_dir}\nerror={exc}"}, form=request.form)


@bp.get("/cleanup")
def cleanup_page():
    return render_template("cleanup.html", result=None, form=request.form)


@bp.post("/cleanup")
def cleanup_submit():
    service = StatsService()
    images_dir = request.form.get("images_dir", "").strip()
    labels_dir = request.form.get("labels_dir", "").strip()
    preview_only = request.form.get("preview_only") == "on"
    try:
        result = service.cleanup_dataset(images_dir, labels_dir, dry_run=preview_only)
        message = "仅预览清理结果" if preview_only else "清理完成"
        debug = _debug_summary("清理调试信息", {**result, "preview_only": preview_only})
        return render_template("cleanup.html", result={"success": True, "message": message, "data": result, "debug": debug}, form=request.form)
    except Exception as exc:
        return render_template("cleanup.html", result={"success": False, "message": str(exc), "data": {}, "debug": f"清理失败\nimages_dir={images_dir}\nlabels_dir={labels_dir}\npreview_only={preview_only}\nerror={exc}"}, form=request.form)
