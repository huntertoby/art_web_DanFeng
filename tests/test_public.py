"""前台：頁面能開、匯入的資料完整、下架作品不會出現。"""
from pathlib import Path

import pytest

from danfeng.extensions import db
from danfeng.models import ALBUMS, Artwork, Photo, Section, Student

PAGES = ["/", "/ambassadors.html", "/artworks.html", "/scene.html", "/opening.html", "/teaching.html"]


@pytest.mark.parametrize("path", PAGES)
def test_page_loads(client, path):
    assert client.get(path).status_code == 200


def test_seed_imports_everything(app):
    assert Section.query.count() == 4
    assert Artwork.query.count() == 25
    assert Student.query.count() == 8
    for album in ALBUMS:
        folder = Path(app.static_folder) / album
        files = [f for f in folder.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]
        assert Photo.query.filter_by(album=album).count() == len(files)


def test_seeded_files_exist(app):
    """資料庫裡記的每個檔案都要真的存在（抓檔名打錯）。"""
    static = Path(app.static_folder)
    paths = [a.image for a in Artwork.query] + [a.audio for a in Artwork.query if a.audio]
    paths += [s.image for s in Student.query] + [p.path for p in Photo.query]
    missing = [p for p in paths if not (static / p).is_file()]
    assert missing == []


def test_qr_code_ids_render(client):
    html = client.get("/artworks.html").get_data(as_text=True)
    assert 'id="art-btn-C-03"' in html


def test_unpublished_artwork_is_hidden(client):
    art = Artwork.query.filter_by(code="C-03").one()
    art.is_published = False
    db.session.commit()
    html = client.get("/artworks.html").get_data(as_text=True)
    assert "art-btn-C-03" not in html
    assert '"C-03"' not in html  # 也不在給 JS 的資料裡，QR Code 打不開


def test_section_without_published_artworks_is_hidden(client):
    section = Section.query.filter_by(name="大師工作坊").one()
    for art in section.artworks:
        art.is_published = False
    db.session.commit()
    assert "大師工作坊" not in client.get("/artworks.html").get_data(as_text=True)
