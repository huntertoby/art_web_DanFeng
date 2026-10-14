"""Flask 擴充套件的單例，於 create_app() 中初始化。"""
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

login_manager = LoginManager()
login_manager.login_view = "admin.login"
login_manager.login_message = "請先登入後台。"
