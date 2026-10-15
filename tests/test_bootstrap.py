"""部署時的自動初始化（danfeng/bootstrap.py）。"""
import logging

from danfeng import create_app
from danfeng.bootstrap import bootstrap
from danfeng.models import Artwork, User


def make_app(tmp_path):
    return create_app({"SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'fresh.db'}", "WTF_CSRF_ENABLED": False})


def test_bootstrap_on_empty_database(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "teacher")
    monkeypatch.setenv("ADMIN_PASSWORD", "super-secret")
    app = make_app(tmp_path)
    bootstrap(app)

    client = app.test_client()
    for path in ["/artworks.html", "/ambassadors.html", "/scene.html"]:
        assert client.get(path).status_code == 200
    response = client.post("/admin/login", data={"username": "teacher", "password": "super-secret"})
    assert response.status_code == 302 and response.headers["Location"] == "/admin/"


def test_bootstrap_is_idempotent_and_keeps_edits(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "teacher")
    monkeypatch.setenv("ADMIN_PASSWORD", "super-secret")
    app = make_app(tmp_path)
    bootstrap(app)
    with app.app_context():
        art = Artwork.query.filter_by(code="C-03").one()
        art.title = "後台改過的標題"
        from danfeng.extensions import db
        db.session.commit()

    bootstrap(app)  # 模擬重新啟動
    with app.app_context():
        assert Artwork.query.count() == 25
        assert Artwork.query.filter_by(code="C-03").one().title == "後台改過的標題"
        assert User.query.count() == 1


def test_bootstrap_updates_admin_password(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "teacher")
    monkeypatch.setenv("ADMIN_PASSWORD", "first-password")
    app = make_app(tmp_path)
    bootstrap(app)
    monkeypatch.setenv("ADMIN_PASSWORD", "second-password")
    bootstrap(app)
    with app.app_context():
        assert User.query.one().check_password("second-password")


def test_bootstrap_rejects_short_password(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "teacher")
    monkeypatch.setenv("ADMIN_PASSWORD", "short")
    app = make_app(tmp_path)
    bootstrap(app)
    with app.app_context():
        assert User.query.count() == 0


def test_bootstrap_keeps_app_logging(tmp_path):
    app = make_app(tmp_path)
    bootstrap(app)
    assert not app.logger.disabled
    assert not logging.getLogger("gunicorn.error").disabled
