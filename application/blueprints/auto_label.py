from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from application.services.auto_label_service import AutoLabelService

bp = Blueprint('auto_label', __name__)


@bp.get('/auto-label')
def auto_label_page():
    service = AutoLabelService()
    models_dir = request.args.get('models_dir', '').strip() or 'models'
    models_result = {'models_dir': models_dir, 'models': []}
    try:
        models_result = service.list_models(models_dir)
    except Exception:
        pass
    return render_template('auto_label.html', result=None, form=request.form, models=models_result)


@bp.post('/auto-label')
def auto_label_submit():
    service = AutoLabelService()
    try:
        result = service.auto_label_images(
            images_dir=request.form.get('images_dir', '').strip(),
            labels_dir=request.form.get('labels_dir', '').strip(),
            model_path=request.form.get('model_path', '').strip(),
            mapping_text=request.form.get('mapping_text', '').strip(),
            class_thresholds_text=request.form.get('class_thresholds_text', '').strip(),
        )
        return render_template('auto_label.html', result={'success': True, 'message': '自动标注完成', 'data': result}, form=request.form, models=service.list_models(request.form.get('models_dir', '').strip() or 'models'))
    except Exception as exc:
        models_result = {'models_dir': request.form.get('models_dir', '').strip() or 'models', 'models': []}
        try:
            models_result = service.list_models(models_result['models_dir'])
        except Exception:
            pass
        return render_template('auto_label.html', result={'success': False, 'message': str(exc), 'data': {}}, form=request.form, models=models_result)


@bp.get('/api/auto-label/models')
def auto_label_models_api():
    service = AutoLabelService()
    models_dir = request.args.get('models_dir', '').strip() or 'models'
    try:
        result = service.list_models(models_dir)
        return jsonify(success=True, data=result)
    except Exception as exc:
        return jsonify(success=False, message=str(exc), data={'models_dir': models_dir, 'models': []}), 400


@bp.post('/api/auto-label/upload-model')
def auto_label_upload_model_api():
    service = AutoLabelService()
    payload = request.get_json(silent=True) or request.form
    try:
        result = service.upload_model(
            source_model_path=(payload.get('source_model_path') or '').strip(),
            models_dir=(payload.get('models_dir') or 'models').strip() or 'models',
            preferred_name=(payload.get('preferred_name') or '').strip() or None,
        )
        return jsonify(success=True, message='模型上传完成', data=result)
    except Exception as exc:
        return jsonify(success=False, message=str(exc), data={}), 400
