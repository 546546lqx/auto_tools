from __future__ import annotations

from flask import Blueprint, render_template, request

from application.services.stats_service import StatsService

bp = Blueprint("cleanup", __name__)


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
        return render_template("cleanup.html", result={"success": True, "message": message, "data": result}, form=request.form)
    except Exception as exc:
        return render_template("cleanup.html", result={"success": False, "message": str(exc), "data": {}}, form=request.form)
