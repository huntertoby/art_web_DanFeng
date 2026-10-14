"""設定值。正式環境用環境變數覆寫：

- DATABASE_URL  資料庫連線字串（未設定時用 instance/site.db 的 SQLite）
- SECRET_KEY    session 簽章金鑰（未設定時自動產生並存在 instance/secret_key）
"""
import os
import secrets
from pathlib import Path


def _database_url(instance_path):
    url = os.environ.get("DATABASE_URL")
    if not url:
        return f"sqlite:///{Path(instance_path) / 'site.db'}"
    # Render / Heroku 給的是 postgres://，SQLAlchemy 2 需要明確指定 driver
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def _secret_key(instance_path):
    key = os.environ.get("SECRET_KEY")
    if key:
        return key
    key_file = Path(instance_path) / "secret_key"
    if not key_file.exists():
        key_file.write_text(secrets.token_hex(32))
    return key_file.read_text().strip()


def load_config(app):
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.config.update(
        SECRET_KEY=_secret_key(app.instance_path),
        SQLALCHEMY_DATABASE_URI=_database_url(app.instance_path),
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 單次上傳上限 50MB（語音檔較大）
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        REMEMBER_COOKIE_HTTPONLY=True,
    )
