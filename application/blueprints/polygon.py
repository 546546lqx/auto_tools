from __future__ import annotations

from pathlib import Path
import socket
import time

import cv2
from flask import Blueprint, jsonify, render_template, request

from application.services.convert_service import ConvertService

bp = Blueprint("polygon", __name__)


@bp.get("/polygon")
def polygon_page():
    return render_template("polygon.html")


@bp.post("/polygon")
def polygon_submit():
    service = ConvertService()
    try:
        result = service.save_polygon(
            image_width=int(request.form.get("image_width", 0)),
            image_height=int(request.form.get("image_height", 0)),
            points_text=request.form.get("points_text", "[]"),
            output_path=request.form.get("output_path", "polygon_coords.txt"),
        )
        return render_template("polygon.html", result={"success": True, "message": "多边形已保存", "data": result})
    except Exception as exc:
        return render_template("polygon.html", result={"success": False, "message": str(exc), "data": {}})


@bp.get("/polygon/frame-preview")
def polygon_frame_preview():
    source = (request.args.get("source") or "").strip()
    if not source:
        return jsonify({"success": False, "message": "缺少 source 参数"}), 400

    preview_dir = Path(__file__).resolve().parents[1] / "static" / "preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    preview_file = preview_dir / "polygon_frame_preview.jpg"

    try:
        if preview_file.exists():
            preview_file.unlink()

        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            return jsonify({"success": False, "message": "无法打开视频流，请检查 RTSP/MP4 地址是否可访问，或确认是否需要鉴权/网络可达"}), 500

        last_error = None
        for attempt in range(1, 4):
            ok, frame = cap.read()
            if ok and frame is not None:
                cv2.imwrite(str(preview_file), frame)
                cap.release()
                return jsonify({"success": True, "image_url": f"/static/preview/{preview_file.name}?t={int(time.time())}", "filename": source, "attempt": attempt})
            last_error = f"第 {attempt} 次读取首帧失败"
            time.sleep(0.35)

        cap.release()
        return jsonify({"success": False, "message": f"视频流打开成功，但没有读到首帧。{last_error}。可能是流尚未就绪、网络超时，或 RTSP 服务器未立即返回图像。"}), 500
    except cv2.error as exc:
        return jsonify({"success": False, "message": f"OpenCV 读取失败：{exc}"}), 500
    except socket.timeout:
        return jsonify({"success": False, "message": "网络超时：RTSP 服务器在规定时间内没有响应"}), 500
    except Exception as exc:
        return jsonify({"success": False, "message": f"首帧提取失败：{exc}"}), 500
