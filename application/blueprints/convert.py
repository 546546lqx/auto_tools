from __future__ import annotations

from flask import Blueprint, render_template, request

from application.services.convert_service import ConvertService

bp = Blueprint("convert", __name__)


@bp.get("/convert")
def convert_page():
    return render_template("convert.html", result=None, form=request.form)


@bp.post("/convert")
def convert_submit():
    service = ConvertService()
    try:
        result = service.convert_dataset(
            source_format=request.form.get("source_format", "VOC"),
            input_dir=request.form.get("input_dir", "").strip(),
            output_dir=request.form.get("output_dir", "").strip() or None,
            class_mapping_text=request.form.get("class_mapping_text", ""),
        )
        return render_template("convert.html", result={"success": True, "message": "转换完成", "data": result}, form=request.form)
    except Exception as exc:
        return render_template("convert.html", result={"success": False, "message": str(exc), "data": {}}, form=request.form)
