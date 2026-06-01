from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path

import cv2
from flask import Blueprint, jsonify, request

bp = Blueprint("rtsp", __name__)


@dataclass
class RTSPJob:
    job_id: str
    rtsp_url: str
    output_dir: str
    segment_minutes: int = 5
    total_duration: float | None = None
    prefix: str = "recording"
    status: str = "pending"
    logs: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    stop_flag: bool = False
    output_files: list[str] = field(default_factory=list)
    error: str | None = None

    def log(self, msg: str):
        self.logs.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
        self.updated_at = time.time()
        self.logs = self.logs[-1000:]


JOBS: dict[str, RTSPJob] = {}
LOCK = threading.Lock()
JOBS_FILE = Path(__file__).resolve().parents[2] / ".state" / "rtsp_jobs.json"


def _jobs_file() -> Path:
    return JOBS_FILE


def _save():
    _jobs_file().parent.mkdir(parents=True, exist_ok=True)
    _jobs_file().write_text(json.dumps({k: asdict(v) for k, v in JOBS.items()}, ensure_ascii=False, indent=2), encoding="utf-8")


def _load():
    if not _jobs_file().exists():
        return
    try:
        raw = json.loads(_jobs_file().read_text(encoding="utf-8"))
        for jid, item in raw.items():
            JOBS[jid] = RTSPJob(**item)
    except Exception:
        pass


@bp.record_once
def _on_register(_state):
    _load()


@bp.post("/start")
def start():
    p = request.get_json(force=True, silent=True) or {}
    rtsp_url = (p.get("rtsp_url") or "").strip()
    if not rtsp_url:
        return _fail("请填写 RTSP 地址")
    job = RTSPJob(
        job_id=str(int(time.time() * 1000)),
        rtsp_url=rtsp_url,
        output_dir=(p.get("output_dir") or "./recordings").strip(),
        segment_minutes=max(1, int(p.get("segment_minutes", 5))),
        total_duration=_float_or_none(p.get("total_duration")),
        prefix=(p.get("prefix") or "recording").strip(),
    )
    job.log("任务已创建，等待启动")
    with LOCK:
        JOBS[job.job_id] = job
        _save()
    threading.Thread(target=_worker, args=(job.job_id,), daemon=True).start()
    return _ok({"job_id": job.job_id}, "录制任务已启动")


@bp.get("/list")
def list_jobs():
    with LOCK:
        jobs = [
            {"job_id": j.job_id, "status": j.status, "created_at": j.created_at, "updated_at": j.updated_at, "prefix": j.prefix, "output_dir": j.output_dir}
            for j in sorted(JOBS.values(), key=lambda x: x.created_at, reverse=True)
        ]
    return _ok({"jobs": jobs}, "任务列表")


@bp.get("/status/<job_id>")
def status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return _fail("任务不存在", 404)
    return _ok({"job_id": job.job_id, "status": job.status, "created_at": job.created_at, "updated_at": job.updated_at, "logs": job.logs[-400:], "output_dir": job.output_dir, "output_files": job.output_files[-50:], "error": job.error, "stop_flag": job.stop_flag}, "任务状态")


@bp.post("/stop/<job_id>")
def stop(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return _fail("任务不存在", 404)
    job.stop_flag = True
    job.log("收到停止请求")
    _save()
    return _ok({"job_id": job.job_id}, "已发送停止请求")


@bp.delete("/delete/<job_id>")
def delete(job_id: str):
    with LOCK:
        if JOBS.pop(job_id, None) is None:
            return _fail("任务不存在", 404)
        _save()
    return _ok({"job_id": job_id}, "任务已删除")


def _worker(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return
    try:
        job.status = "running"
        job.log(f"开始录制：{job.rtsp_url}")
        _save()
        out_dir = Path(job.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        cap = cv2.VideoCapture(job.rtsp_url, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            raise RuntimeError("无法打开 RTSP 流")
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1280)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 720)
        segment_frames = max(1, int(fps * job.segment_minutes * 60))
        total_limit = int(fps * float(job.total_duration) * 60) if job.total_duration else None
        frame_count = 0
        total_written = 0
        segment_index = 0
        out = None
        current_filename = None
        while not job.stop_flag:
            ret, frame = cap.read()
            if not ret:
                job.log("读取失败，尝试重连")
                cap.release()
                time.sleep(5)
                cap = cv2.VideoCapture(job.rtsp_url, cv2.CAP_FFMPEG)
                continue
            if out is None or frame_count >= segment_frames:
                if out is not None:
                    out.release()
                    if current_filename:
                        job.output_files.append(current_filename)
                current_filename = str(out_dir / f"{job.prefix}_{time.strftime('%Y%m%d_%H%M%S')}_{segment_index + 1:03d}.mp4")
                out = cv2.VideoWriter(current_filename, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
                if not out.isOpened():
                    raise RuntimeError(f"无法创建输出文件：{current_filename}")
                segment_index += 1
                frame_count = 0
                job.log(f"开始新分段：{Path(current_filename).name}")
            out.write(frame)
            frame_count += 1
            total_written += 1
            if total_limit and total_written >= total_limit:
                job.log("达到总时长限制，准备停止")
                break
            if total_written % max(1, int(fps * 5)) == 0:
                job.log(f"已录制约 {total_written / fps:.1f} 秒")
                _save()
        job.status = "stopped" if job.stop_flag else "finished"
        job.log(f"录制结束，总帧数：{total_written}")
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        job.log(f"录制异常：{e}")
    finally:
        try:
            if out is not None:
                out.release()
            cap.release()
        except Exception:
            pass
        _save()


def _ok(data=None, message="ok"):
    return jsonify({"success": True, "message": message, "data": data or {}})


def _fail(message, code=400):
    return jsonify({"success": False, "message": message, "data": {}}), code


def _float_or_none(value):
    if value in (None, "", "null"):
        return None
    return float(value)
