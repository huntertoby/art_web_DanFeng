"""前台頁面。網址保留 .html 結尾，因為展場的 QR Code 與分享連結都指向這些網址。"""
from flask import Blueprint, render_template

from .models import Artwork, Photo, Section, Student

bp = Blueprint("public", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/ambassadors.html")
def ambassadors():
    """(一) 廣達藝術小尖兵：成員介紹 + 兩天培訓的照片。"""
    return render_template(
        "ambassadors.html",
        students=Student.query.order_by(Student.sort_order).all(),
        museum_photos=Photo.in_album("a"),
        training_photos=Photo.in_album("b"),
    )


@bp.route("/artworks.html")
def artworks():
    """(二) 義大利文藝復興作品。支援 ?art=<作品編號> 直接打開該作品（展場 QR Code 用）。"""
    sections = [
        (section, section.published_artworks())
        for section in Section.query.order_by(Section.sort_order)
    ]
    sections = [(section, arts) for section, arts in sections if arts]
    artworks_by_code = {art.code: art.to_public_dict() for _, arts in sections for art in arts}
    return render_template("artworks.html", sections=sections, artworks_by_code=artworks_by_code)


@bp.route("/scene.html")
def scene():
    """(三) 展覽現場。"""
    return render_template("scene.html", photos=Photo.in_album("scene"))


@bp.route("/opening.html")
def opening():
    """(四) 開幕典禮。"""
    return render_template("opening.html", photos=Photo.in_album("opening"))


@bp.route("/teaching.html")
def teaching():
    """(五) 展覽與教學。"""
    return render_template("teaching.html", photos=Photo.in_album("teaching"))
