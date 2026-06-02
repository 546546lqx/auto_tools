from __future__ import annotations

import argparse
import json
from pathlib import Path

from flask import Blueprint, Flask, jsonify, request

bp = Blueprint('desktop_picker', __name__)


def _pick_path(selection_type: str) -> str:
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.update()

    try:
        if selection_type == 'directory':
            path = filedialog.askdirectory(title='请选择本地目录')
        elif selection_type == 'file':
            path = filedialog.askopenfilename(title='请选择文件')
        else:
            raise ValueError("selection_type must be 'directory' or 'file'")
    finally:
        root.destroy()

    return path or ''


@bp.post('/api/desktop-picker')
def desktop_picker():
    payload = request.get_json(silent=True) or {}
    selection_type = payload.get('selection_type', 'directory')
    if selection_type not in {'directory', 'file'}:
        return jsonify(success=False, message='selection_type must be directory or file'), 400

    try:
        path = _pick_path(selection_type)
    except Exception as exc:
        return jsonify(success=False, message=f'无法打开选择器: {exc}'), 500

    response = {
        'success': bool(path),
        'type': selection_type,
        'path': path,
        'exists': Path(path).exists() if path else False,
        'is_dir': Path(path).is_dir() if path else False,
        'is_file': Path(path).is_file() if path else False,
    }
    return jsonify(response), 200 if path else 400


def main() -> int:
    parser = argparse.ArgumentParser(description='Open a native file or folder picker and print the selected path.')
    parser.add_argument('--type', choices=('directory', 'file'), default='directory', help='Selection type')
    parser.add_argument('--json', action='store_true', help='Print JSON payload instead of raw path')
    args = parser.parse_args()

    path = _pick_path(args.type)
    payload = {
        'success': bool(path),
        'type': args.type,
        'path': path,
        'exists': Path(path).exists() if path else False,
        'is_dir': Path(path).is_dir() if path else False,
        'is_file': Path(path).is_file() if path else False,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(path)

    return 0 if path else 1


if __name__ == '__main__':
    raise SystemExit(main())
