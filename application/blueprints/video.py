from __future__ import annotations

import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

from flask import Blueprint, jsonify, render_template, request

from application.services.video_service import VideoService

bp = Blueprint("video", __name__)
_executor = ThreadPoolExecutor(max_workers=2)
_jobs: dict[str, dict] = {}


@bp.get("/video")
def video_page():
    return render_template("video.html", result=None, form=request.form)


@bp.post("/api/video/start")
def video_start():
    payload = request.get_json(silent=True) or request.form
    source = str(payload.get("source", "")).strip()
    output_dir = str(payload.get("output_dir", "")).strip()
    interval = int(payload.get("interval", 30))
    output_format = str(payload.get("output_format", "jpg")).strip() or "jpg"
    service = VideoService()
    job_id = uuid.uuid4().hex
    stop_event = threading.Event()
    job = {
        "job_id": job_id,
        "status": "running",
        "progress": 0,
        "message": "正在抽帧，请稍候...",
        "result": None,
        "source": source,
        "source_name": source.rsplit("/", 1)[-1] if source else "",
        "output_dir": output_dir,
        "interval": interval,
        "output_format": output_format,
        "stop_event": stop_event,
    }
    _jobs[job_id] = job

    def _progress(data):
        job["progress"] = data.get("current_frame", job["progress"])
        job["saved_count"] = data.get("saved", job.get("saved_count", 0))
        job["total_frames"] = data.get("total_frames", job.get("total_frames", 0))
        job["stopped"] = data.get("stopped", job.get("stopped", False))

    def _run():
        try:
            result = service.extract_frames(source, output_dir, interval=interval, output_format=output_format, stop_event=stop_event, progress_callback=_progress)
            job["status"] = "stopped" if result.get("stopped") else "completed"
            job["result"] = result
            job["saved_count"] = result.get("saved_count", len(result.get("saved", [])))
            job["total_frames"] = result.get("total_frames", job.get("total_frames", 0))
            job["stopped"] = result.get("stopped", False)
            job["message"] = "抽帧已停止，已保存的数据仍保留。" if result.get("stopped") else "抽帧完成"
        except Exception as exc:
            job["status"] = "failed"
            job["message"] = str(exc)
        finally:
            job["done"] = True

    _executor.submit(_run)
    return jsonify({"success": True, "job_id": job_id, "message": "任务已启动"})


@bp.get("/api/video/status/<job_id>")
def video_status(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        return jsonify({"success": False, "message": "任务不存在"}), 404
    return jsonify({"success": True, "data": {k: v for k, v in job.items() if k != "stop_event"}})


@bp.post("/api/video/stop/<job_id>")
def video_stop(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        return jsonify({"success": False, "message": "任务不存在"}), 404
    stop_event = job.get("stop_event")
    if stop_event:
        stop_event.set()
        job["status"] = "stopping"
        job["message"] = "正在停止抽帧..."
    return jsonify({"success": True, "message": "已发送停止请求"})
