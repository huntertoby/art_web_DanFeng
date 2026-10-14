"""後台：權限、CRUD、上傳、安全。"""
from pathlib import Path

import pytest

from danfeng import create_app
from danfeng.extensions import db
from danfeng.models import Artwork, Photo, Section, Student

from .conftest import ADMIN_PASSWORD, fake_file

ADMIN_PAGES = ["/admin/", "/admin/artworks", "/admin/artworks/new", "/admin/sections",
               "/admin/students", "/admin/students/new", "/admin/photos", "/admin/photos/scene"]


def artwork_form(**overrides):
    data = {
        "code": "Z-01", "section_id": Section.query.first().id, "title": "測試作品",
        "artist": "測試藝術家", "year": "2026", "location": "", "description": "賞析內容",
        "answer": "解答", "student_name": "", "is_published": "y",
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------- 權限

@pytest.mark.parametrize("path", ADMIN_PAGES)
def test_admin_requires_login(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


@pytest.mark.parametrize("path", ADMIN_PAGES)
def test_admin_pages_load_when_logged_in(admin_client, path):
    assert admin_client.get(path).status_code == 200


def test_post_routes_also_require_login(client):
    art = Artwork.query.first()
    response = client.post(f"/admin/artworks/{art.id}/delete")
    assert response.status_code == 302
    assert db.session.get(Artwork, art.id) is not None


def test_wrong_password(client):
    response = client.post("/admin/login", data={"username": "admin", "password": "nope"})
    assert "帳號或密碼錯誤" in response.get_data(as_text=True)


def test_login_redirects_to_next(client):
    response = client.post("/admin/login?next=/admin/students",
                           data={"username": "admin", "password": ADMIN_PASSWORD})
    assert response.headers["Location"] == "/admin/students"


@pytest.mark.parametrize("evil", ["https://evil.example", "//evil.example", "javascript:alert(1)"])
def test_login_ignores_external_next(client, evil):
    response = client.post(f"/admin/login?next={evil}",
                           data={"username": "admin", "password": ADMIN_PASSWORD})
    assert response.headers["Location"] == "/admin/"


def test_logout_requires_post(admin_client):
    assert admin_client.get("/admin/logout").status_code == 405
    admin_client.post("/admin/logout")
    assert admin_client.get("/admin/").status_code == 302


def test_csrf_is_enforced():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
    with app.app_context():
        db.create_all()
        response = app.test_client().post("/admin/login", data={"username": "a", "password": "b"})
        assert response.status_code == 400


# ---------------------------------------------------------------- 作品

def test_create_artwork(admin_client, upload_root):
    response = admin_client.post("/admin/artworks/new", data={
        **artwork_form(), "image": fake_file("聖殤.JPG"), "audio": fake_file("導覽.mp3"),
    }, content_type="multipart/form-data")
    assert response.status_code == 302

    art = Artwork.query.filter_by(code="Z-01").one()
    assert art.image.startswith("uploads/artworks/") and art.image.endswith(".jpg")
    assert (upload_root / art.image).is_file()
    assert (upload_root / art.audio).is_file()
    assert "art-btn-Z-01" in admin_client.get("/artworks.html").get_data(as_text=True)


def test_create_artwork_requires_image(admin_client, upload_root):
    response = admin_client.post("/admin/artworks/new", data=artwork_form(), content_type="multipart/form-data")
    assert "新作品必須上傳圖片" in response.get_data(as_text=True)
    assert Artwork.query.filter_by(code="Z-01").first() is None


def test_rejects_wrong_file_type(admin_client, upload_root):
    response = admin_client.post("/admin/artworks/new", data={
        **artwork_form(), "image": fake_file("hack.php"),
    }, content_type="multipart/form-data")
    assert "圖片只接受" in response.get_data(as_text=True)
    assert not (upload_root / "uploads").exists()


def test_rejects_duplicate_code(admin_client, upload_root):
    response = admin_client.post("/admin/artworks/new", data={
        **artwork_form(code="C-03"), "image": fake_file("a.jpg"),
    }, content_type="multipart/form-data")
    assert "編號已被" in response.get_data(as_text=True)


def test_edit_without_new_file_keeps_image(admin_client):
    art = Artwork.query.filter_by(code="C-03").one()
    original_image = art.image
    admin_client.post(f"/admin/artworks/{art.id}/edit",
                      data=artwork_form(code="C-03", title="新標題", section_id=art.section_id),
                      content_type="multipart/form-data")
    db.session.refresh(art)
    assert art.title == "新標題"
    assert art.image == original_image


def test_replacing_upload_deletes_old_upload(admin_client, upload_root):
    admin_client.post("/admin/artworks/new", data={**artwork_form(), "image": fake_file("a.jpg")},
                      content_type="multipart/form-data")
    art = Artwork.query.filter_by(code="Z-01").one()
    first_image = upload_root / art.image

    admin_client.post(f"/admin/artworks/{art.id}/edit",
                      data={**artwork_form(), "image": fake_file("b.png")},
                      content_type="multipart/form-data")
    db.session.refresh(art)
    assert not first_image.exists()
    assert (upload_root / art.image).is_file()


def test_seeded_originals_are_never_deleted(admin_client, upload_root):
    """原始素材在 git 裡，換圖或刪除作品都不能刪到它。"""
    original = upload_root / "21聖殤.jpg"
    original.write_bytes(b"original")
    art = Artwork.query.filter_by(code="D-02").one()
    admin_client.post(f"/admin/artworks/{art.id}/delete")
    assert original.exists()


def test_remove_audio(admin_client):
    art = Artwork.query.filter_by(code="C-03").one()
    admin_client.post(f"/admin/artworks/{art.id}/edit",
                      data=artwork_form(code="C-03", section_id=art.section_id, remove_audio="y"),
                      content_type="multipart/form-data")
    db.session.refresh(art)
    assert art.audio == ""


def test_toggle_publish(admin_client):
    art = Artwork.query.filter_by(code="C-03").one()
    admin_client.post(f"/admin/artworks/{art.id}/toggle")
    db.session.refresh(art)
    assert art.is_published is False


def test_move_artwork(admin_client):
    section = Section.query.filter_by(name="超級比一比").one()
    first, second = section.artworks[0], section.artworks[1]
    admin_client.post(f"/admin/artworks/{first.id}/move/down")
    db.session.expire_all()
    assert [a.code for a in section.artworks[:2]] == [second.code, first.code]


def test_moving_to_another_section_appends_to_end(admin_client):
    art = Artwork.query.filter_by(code="B-02").one()
    target = Section.query.filter_by(name="大師工作坊").one()
    admin_client.post(f"/admin/artworks/{art.id}/edit",
                      data=artwork_form(code="B-02", section_id=target.id),
                      content_type="multipart/form-data")
    db.session.expire_all()
    assert target.artworks[-1].code == "B-02"


# ---------------------------------------------------------------- 分區

def test_create_and_rename_section(admin_client):
    admin_client.post("/admin/sections", data={"name": "新分區"})
    section = Section.query.filter_by(name="新分區").one()
    admin_client.post(f"/admin/sections/{section.id}/rename", data={"name": "改過的名字"})
    db.session.refresh(section)
    assert section.name == "改過的名字"


def test_cannot_delete_section_with_artworks(admin_client):
    section = Section.query.first()
    response = admin_client.post(f"/admin/sections/{section.id}/delete", follow_redirects=True)
    assert "請先移走或刪除" in response.get_data(as_text=True)
    assert db.session.get(Section, section.id) is not None


def test_delete_empty_section(admin_client):
    admin_client.post("/admin/sections", data={"name": "空分區"})
    section = Section.query.filter_by(name="空分區").one()
    admin_client.post(f"/admin/sections/{section.id}/delete")
    assert db.session.get(Section, section.id) is None


# ---------------------------------------------------------------- 小尖兵、相簿

def test_create_student(admin_client, upload_root):
    admin_client.post("/admin/students/new", data={
        "name": "王O明", "quote": "很好玩", "image": fake_file("me.jpg"),
    }, content_type="multipart/form-data")
    student = Student.query.filter_by(name="王O明").one()
    assert student.sort_order == 8
    assert "王O明" in admin_client.get("/ambassadors.html").get_data(as_text=True)


def test_upload_and_delete_photos(admin_client, upload_root):
    before = Photo.query.filter_by(album="scene").count()
    admin_client.post("/admin/photos/scene", data={
        "photos": [fake_file("1.jpg"), fake_file("2.webp")],
    }, content_type="multipart/form-data")
    photos = Photo.in_album("scene")
    assert len(photos) == before + 2

    newest = photos[-1]
    assert (upload_root / newest.path).is_file()
    admin_client.post(f"/admin/photos/item/{newest.id}/delete")
    assert not (upload_root / newest.path).exists()
    assert Photo.query.filter_by(album="scene").count() == before + 1


def test_unknown_album_is_404(admin_client):
    assert admin_client.get("/admin/photos/nope").status_code == 404
