from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from application.services.split_service import SplitService

bp = Blueprint("rename", __name__)


@bp.get("/rename")
def rename_page():
    return render_template("rename.html", result=None, form=request.form)


@bp.post("/rename")
def rename_submit():
    service = SplitService()
    try:
        result = service.rename_pairs(
            images_dir=request.form.get("images_dir", "").strip(),
            labels_dir=request.form.get("labels_dir", "").strip(),
            prefix=request.form.get("prefix", "frame_by"),
            start=int(request.form.get("start", 1)),
            digit=int(request.form.get("digit", 6)),
            dry_run=request.form.get("dry_run") == "on",
        )
        return render_template("rename.html", result={"success": True, "message": "重命名完成", "data": result}, form=request.form)
    except Exception as exc:
        return render_template("rename.html", result={"success": False, "message": str(exc), "data": {}}, form=request.form)


@bp.post("/api/rename-pairs")
def api_rename_pairs():
    service = SplitService()
    payload = request.get_json(silent=True) or {}
    try:
        result = service.rename_pairs(
            images_dir=(payload.get("images_dir") or "").strip(),
            labels_dir=(payload.get("labels_dir") or "").strip(),
            prefix=(payload.get("prefix") or "frame_by").strip() or "frame_by",
            start=int(payload.get("start", 1)),
            digit=int(payload.get("digit", 6)),
            dry_run=bool(payload.get("dry_run", False)),
        )
        return jsonify(success=True, message="重命名完成", data=result)
    except Exception as exc:
        return jsonify(success=False, message=str(exc), data={}), 400
