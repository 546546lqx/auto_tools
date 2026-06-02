from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from application.utils.file_helper import require_existing_path, require_text

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'}
MODEL_EXTENSIONS = {'.pt', '.onnx', '.engine', '.tflite'}


@dataclass
class AutoLabelService:
    """Automatic YOLO label generation with a local custom model.

    The service scans a model directory, optionally copies an uploaded model into it,
    then runs inference on every image inside the images directory and writes YOLO txt
    files to the labels directory.
    """

    def list_models(self, models_dir: str) -> dict:
        """List available model files under a local models directory."""
        models_path = Path(require_existing_path(models_dir, 'models 文件夹'))
        if not models_path.is_dir():
            raise NotADirectoryError(f'路径不是文件夹：{models_path}')

        models = []
        for path in sorted(models_path.rglob('*')):
            if path.is_file() and path.suffix.lower() in MODEL_EXTENSIONS:
                rel_path = path.relative_to(models_path)
                models.append({
                    'name': path.name,
                    'display_name': path.name,
                    'path': str(path),
                    'relative_path': str(rel_path),
                })
        return {'models_dir': str(models_path), 'models': models}

    def upload_model(self, source_model_path: str, models_dir: str, preferred_name: str | None = None) -> dict:
        """Copy a user-selected model into the models directory without overwriting existing files."""
        source = require_existing_path(source_model_path, '模型文件')
        if not source.is_file():
            raise FileNotFoundError(f'模型文件不存在：{source}')
        if source.suffix.lower() not in MODEL_EXTENSIONS:
            raise ValueError(f'不支持的模型格式：{source.suffix}')

        models_path = Path(require_existing_path(models_dir, 'models 文件夹'))
        if not models_path.is_dir():
            raise NotADirectoryError(f'路径不是文件夹：{models_path}')
        models_path.mkdir(parents=True, exist_ok=True)

        candidate = self._build_unique_target(models_path, preferred_name or source.name)
        shutil.copy2(source, candidate)
        return {'uploaded_path': str(candidate), 'model_name': candidate.name, 'models_dir': str(models_path)}

    def auto_label_images(
        self,
        images_dir: str,
        labels_dir: str,
        model_path: str,
        mapping_text: str,
        classes_output_name: str = 'classes.txt',
        overwrite: bool = True,
    ) -> dict:
        """Run prediction and save YOLO labels for every image.

        Raises:
            ValueError: if mapping text is invalid or no supported model backend is available.
            FileNotFoundError: if any required path does not exist.
            RuntimeError: if the model cannot be loaded or inference fails.
        """
        images_path = require_existing_path(images_dir, 'images 文件夹')
        labels_path = Path(require_text(labels_dir, 'labels 文件夹'))
        labels_path.mkdir(parents=True, exist_ok=True)
        model_file = require_existing_path(model_path, '模型文件')
        if not model_file.is_file():
            raise FileNotFoundError(f'模型文件不存在：{model_file}')

        mapping = self._parse_mapping_text(mapping_text)
        if not mapping:
            raise ValueError('请填写类别映射关系，例如：person-->0\ncar-->1')

        classes_file = labels_path / classes_output_name
        classes_text = self._mapping_to_classes_text(mapping)
        classes_file.write_text(classes_text, encoding='utf-8')

        predictor = self._load_predictor(model_file)
        image_files = self._collect_images(images_path)
        if not image_files:
            raise ValueError('images 文件夹中未找到图片')

        created_labels = []
        empty_labels = []
        for image_file in image_files:
            rel = image_file.relative_to(images_path)
            label_file = labels_path / rel.with_suffix('.txt')
            label_file.parent.mkdir(parents=True, exist_ok=True)

            predictions = predictor.predict(str(image_file))
            lines = self._predictions_to_yolo_lines(predictions, mapping)
            if lines:
                label_file.write_text('\n'.join(lines) + '\n', encoding='utf-8')
            else:
                label_file.write_text('', encoding='utf-8')
                empty_labels.append(str(label_file))
            created_labels.append(str(label_file))

        return {
            'images_dir': str(images_path),
            'labels_dir': str(labels_path),
            'model_path': str(model_file),
            'classes_file': str(classes_file),
            'images_count': len(image_files),
            'labels_count': len(created_labels),
            'empty_labels': empty_labels,
            'created_labels': created_labels,
            'mapping': mapping,
        }

    def _collect_images(self, images_path: Path) -> list[Path]:
        return [p for p in sorted(images_path.rglob('*')) if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]

    def _build_unique_target(self, models_path: Path, filename: str) -> Path:
        candidate = models_path / Path(filename).name
        stem = candidate.stem
        suffix = candidate.suffix
        index = 1
        while candidate.exists():
            candidate = models_path / f'{stem}_{index}{suffix}'
            index += 1
        return candidate

    def _parse_mapping_text(self, text: str) -> dict[str, int]:
        mapping: dict[str, int] = {}
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if '-->' in line:
                left, right = line.split('-->', 1)
            elif '->' in line:
                left, right = line.split('->', 1)
            elif ':' in line:
                left, right = line.split(':', 1)
            else:
                raise ValueError(f'无法解析映射行：{line}')
            name = left.strip()
            if not name:
                raise ValueError(f'类别名不能为空：{line}')
            idx = int(right.strip())
            mapping[name] = idx
        return dict(sorted(mapping.items(), key=lambda item: item[1]))

    def _mapping_to_classes_text(self, mapping: dict[str, int]) -> str:
        if not mapping:
            return ''
        max_index = max(mapping.values())
        classes = [''] * (max_index + 1)
        for name, idx in mapping.items():
            classes[idx] = name
        if any(not name for name in classes):
            missing = [str(idx) for idx, name in enumerate(classes) if not name]
            raise ValueError(f'映射关系缺少类别：{", ".join(missing)}')
        return '\n'.join(classes)

    def _load_predictor(self, model_file: Path):
        try:
            from ultralytics import YOLO  # type: ignore
        except Exception as exc:  # pragma: no cover - runtime dependency guard
            raise RuntimeError('当前环境未安装 ultralytics，无法执行自动标注') from exc

        try:
            model = YOLO(str(model_file))
        except Exception as exc:
            raise RuntimeError(f'模型加载失败：{exc}') from exc

        class _Predictor:
            def __init__(self, yolo_model):
                self.model = yolo_model

            def predict(self, image_path: str):
                return self.model.predict(source=image_path, verbose=False)

        return _Predictor(model)

    def _predictions_to_yolo_lines(self, predictions: Iterable, mapping: dict[str, int]) -> list[str]:
        lines: list[str] = []
        allowed_names = {name.lower(): idx for name, idx in mapping.items()}
        for result in predictions:
            boxes = getattr(result, 'boxes', None)
            if boxes is None:
                continue
            xywhn = getattr(boxes, 'xywhn', None)
            cls_list = getattr(boxes, 'cls', None)
            if xywhn is None or cls_list is None:
                continue
            names = getattr(result, 'names', None)
            xywhn_data = xywhn.tolist() if hasattr(xywhn, 'tolist') else xywhn
            cls_data = cls_list.tolist() if hasattr(cls_list, 'tolist') else cls_list
            for box, cls_id in zip(xywhn_data, cls_data):
                cls_id_int = int(cls_id)
                class_name = self._resolve_class_name(names, cls_id_int)
                mapped_id = allowed_names.get(class_name.lower()) if class_name else None
                if mapped_id is None:
                    continue
                x, y, w, h = [float(v) for v in box]
                lines.append(f'{mapped_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}')
        return lines

    def _resolve_class_name(self, names, class_id: int) -> str:
        if isinstance(names, dict):
            value = names.get(class_id, '')
            return str(value) if value is not None else ''
        if isinstance(names, (list, tuple)) and 0 <= class_id < len(names):
            value = names[class_id]
            return str(value) if value is not None else ''
        return ''
