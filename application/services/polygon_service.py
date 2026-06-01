from __future__ import annotations

import json
from dataclasses import dataclass

from tools.web_tools import polygon_from_points


@dataclass+
class PolygonService:
    def save_polygon(self, image_width: int, image_height: int, points_text: str, output_path: str):
        points = json.loads(points_text) if points_text.strip() else []
        return polygon_from_points(image_width=image_width, image_height=image_height, points=points, output_path=output_path)
