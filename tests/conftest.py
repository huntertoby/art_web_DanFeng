import io

import pytest

from danfeng import create_app
from danfeng.cli import seed_database
from danfeng.extensions import db
from danfeng.models import User

ADMIN_PASSWORD = "correct-horse"


@pytest.fixture
def app():
    """記憶體 SQLite + 匯入真實的 content/*.json 與相簿資料。"""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "WTF_CSRF_ENABLED": False,
    })
    with app.app_context():
        db.create_all()
        seed_database()
        admin = User(username="admin")
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        yield app
        db.session.remove()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_client(client):
    client.post("/admin/login", data={"username": "admin", "password": ADMIN_PASSWORD})
    return client


@pytest.fixture
def upload_root(app, tmp_path):
    """上傳的檔案寫到暫存資料夾，不污染專案的 static/。"""
    original = app.static_folder
    app.static_folder = str(tmp_path)
    yield tmp_path
    app.static_folder = original


def fake_file(name, content=b"fake-bytes"):
    return (io.BytesIO(content), name)
