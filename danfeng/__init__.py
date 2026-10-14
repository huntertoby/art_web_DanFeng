"""丹鳳高中 114 學年度廣達「游於藝」義大利文藝復興展 — 展覽網站。"""
from pathlib import Path

from flask import Flask

from .config import load_config
from .extensions import csrf, db, login_manager, migrate

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def create_app(test_config=None):
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "templates"),
        static_folder=str(PROJECT_ROOT / "static"),
        instance_path=str(PROJECT_ROOT / "instance"),
    )
    load_config(app)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db, directory=str(PROJECT_ROOT / "migrations"), render_as_batch=True)
    csrf.init_app(app)
    login_manager.init_app(app)

    from . import models

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(models.User, int(user_id))

    from .admin import bp as admin_bp
    from .public import bp as public_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    from .cli import register_commands

    register_commands(app)
    return app
