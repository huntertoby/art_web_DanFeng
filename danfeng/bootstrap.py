"""啟動時自動準備資料庫，讓部署不需要手動進 Shell 執行指令。

做三件事（每一步都可重複執行，不會重複匯入或覆蓋資料）：
1. flask db upgrade：建立／更新資料表
2. 資料庫還是空的 → 匯入 content/*.json 與相簿照片（等同 flask seed）
3. 有設定 ADMIN_USERNAME 與 ADMIN_PASSWORD 環境變數 → 建立該管理員；
   帳號已存在但密碼不同 → 更新為環境變數的密碼

只在 Render（環境變數 RENDER 會被自動設定）或設定 AUTO_BOOTSTRAP=1 時執行，
本機開發與測試不受影響。
"""
import os

from flask_migrate import upgrade

from .cli import seed_database
from .extensions import db
from .models import Photo, Section, Student, User


def should_bootstrap():
    return bool(os.environ.get("RENDER") or os.environ.get("AUTO_BOOTSTRAP"))


def bootstrap(app):
    with app.app_context():
        upgrade()

        if not (Section.query.first() or Student.query.first() or Photo.query.first()):
            counts = seed_database()
            app.logger.warning("資料庫為空，已自動匯入初始資料：%s", counts)

        username = os.environ.get("ADMIN_USERNAME")
        password = os.environ.get("ADMIN_PASSWORD")
        if username and password:
            if len(password) < 8:
                app.logger.error("ADMIN_PASSWORD 少於 8 個字元，未建立管理員")
                return
            user = User.query.filter_by(username=username).first()
            if user is None:
                user = User(username=username)
                db.session.add(user)
            if not user.password_hash or not user.check_password(password):
                user.set_password(password)
                db.session.commit()
                app.logger.warning("已依環境變數設定管理員帳號：%s", username)
