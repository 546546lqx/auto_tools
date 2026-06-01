from __future__ import annotations

from flask import Blueprint, render_template, request

from application.services.video_service import VideoService

bp = Blueprint("video", __name__)


@bp.get("/video")
def video_page():
    return render_template("video.html", result=None, form=request.form)


@bp.post("/video")
def video_submit():
    service = VideoService()
    try:
        result = service.extract_frames(
            source=request.form.get("source", "").strip(),
            output_dir=request.form.get("output_dir", "").strip(),
            interval=int(request.form.get("interval", 30)),
            output_format=request.form.get("output_format", "jpg"),
        )
        return render_template("video.html", result={"success": True, "message": "抽帧完成", "data": result}, form=request.form)
    except Exception as exc:
        return render_template("video.html", result={"success": False, "message": str(exc), "data": {}}, form=request.form)
