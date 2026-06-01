from __future__ import annotations

from flask import Blueprint, render_template, request

from application.services.split_service import SplitService

bp = Blueprint("split", __name__)


@bp.get("/split")
def split_page():
    return render_template("split.html", result=None, form=request.form)


@bp.post("/split")
def split_submit():
    service = SplitService()
    try:
        result = service.split_dataset(
            data_root=request.form.get("data_root", "").strip(),
            train_ratio=float(request.form.get("train_ratio", 0.8)),
            val_ratio=float(request.form.get("val_ratio", 0.2)),
            rename_files=request.form.get("rename_files") == "on",
        )
        return render_template("split.html", result={"success": True, "message": "划分完成", "data": result}, form=request.form)
    except Exception as exc:
        return render_template("split.html", result={"success": False, "message": str(exc), "data": {}}, form=request.form)


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
