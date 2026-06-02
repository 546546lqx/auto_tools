from __future__ import annotations

from flask import Flask

from application.blueprints import register_blueprints
from application.config import Config


def create_app(config_object: type[Config] | None = None) -> Flask:
    """Application factory for the YOLO Flask app."""
    app = Flask(
        __name__,
        template_folder=str(Config.BASE_DIR / "application" / "templates"),
        static_folder=str(Config.BASE_DIR / "application" / "static"),
        static_url_path="/static",
    )

    config_cls = config_object or Config
    app.config.from_object(config_cls)

    register_blueprints(app)
    return app
