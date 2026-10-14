"""資料表定義。

圖片、音檔欄位存的是「相對於 static/ 的路徑」，例如：
- 原本就在 git 裡的素材：`21聖殤.jpg`、`scene/LINE_ALBUM_展覽會場_260304_1.jpg`
- 後台上傳的檔案：`uploads/artworks/3f2a….jpg`
"""
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db

# 相簿代號 → 後台顯示名稱。代號同時也是 static/ 底下原始照片的資料夾名稱。
ALBUMS = {
    "a": "小尖兵培訓：美術館參訪",
    "b": "小尖兵培訓：導覽培訓課程",
    "scene": "展覽現場",
    "opening": "開幕典禮",
    "teaching": "展覽與教學",
}


def _now():
    return datetime.now(timezone.utc)


class SortableMixin:
    """有 sort_order 欄位、可在後台上下移動的資料。"""

    sort_order = db.Column(db.Integer, nullable=False, default=0)

    def sibling_query(self):
        """同一組可互相排序的資料（例如同一分區的作品）。子類別視需要覆寫。"""
        return type(self).query

    def next_sort_order(self):
        last = self.sibling_query().order_by(type(self).sort_order.desc()).first()
        return (last.sort_order + 1) if last else 0


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Section(SortableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    artworks = db.relationship("Artwork", back_populates="section", order_by="Artwork.sort_order")

    def published_artworks(self):
        return [art for art in self.artworks if art.is_published]


class Artwork(SortableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # 展場 QR Code 用，例如 C-03
    section_id = db.Column(db.Integer, db.ForeignKey("section.id"), nullable=False)
    section = db.relationship("Section", back_populates="artworks")

    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False, default="")
    year = db.Column(db.String(50), nullable=False, default="")
    location = db.Column(db.String(200), nullable=False, default="")
    description = db.Column(db.Text, nullable=False, default="")
    answer = db.Column(db.Text, nullable=False, default="")  # 「思考時刻」解答
    image = db.Column(db.String(300), nullable=False)
    audio = db.Column(db.String(300), nullable=False, default="")
    student_name = db.Column(db.String(50), nullable=False, default="")  # 錄製語音導覽的小尖兵

    is_published = db.Column(db.Boolean, nullable=False, default=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    def sibling_query(self):
        return Artwork.query.filter_by(section_id=self.section_id)

    def to_public_dict(self):
        """前台作品彈窗需要的資料（給 static/js/artworks.js）。"""
        return {
            "title": self.title,
            "artist": self.artist,
            "year": self.year,
            "location": self.location,
            "desc": self.description,
            "answer": self.answer,
            "img": self.image,
            "audio": self.audio,
            "student_name": self.student_name,
        }


class Student(SortableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    quote = db.Column(db.Text, nullable=False, default="")
    image = db.Column(db.String(300), nullable=False)


class Photo(SortableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    album = db.Column(db.String(20), nullable=False, index=True)
    path = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)

    def sibling_query(self):
        return Photo.query.filter_by(album=self.album)

    @staticmethod
    def in_album(album):
        return Photo.query.filter_by(album=album).order_by(Photo.sort_order).all()
