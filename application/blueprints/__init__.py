from __future__ import annotations

from flask import Flask

from application.blueprints.convert import bp as convert_bp
from application.blueprints.home import bp as home_bp
from application.blueprints.polygon import bp as polygon_bp
from application.blueprints.split import bp as split_bp
from application.blueprints.stats import bp as stats_bp
from application.blueprints.rtsp import bp as rtsp_bp
from application.blueprints.video import bp as video_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(home_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(split_bp)
    app.register_blueprint(convert_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(polygon_bp)
    app.register_blueprint(rtsp_bp, url_prefix="/api/rtsp")
