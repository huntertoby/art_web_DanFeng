from flask import Blueprint

bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder=None)

from . import routes  # noqa: E402,F401  註冊路由
