"""命令列指令：

    flask --app app seed            把 content/*.json 與 static/ 下的相簿照片匯入資料庫
    flask --app app seed --reset    清空作品／小尖兵／相簿後重新匯入
    flask --app app create-admin 帳號   建立管理員（或重設密碼）
"""
import json
from pathlib import Path

import click
from flask import current_app
from sqlalchemy import inspect

from .extensions import db
from .models import ALBUMS, Artwork, Photo, Section, Student, User

IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")


def _load_json(name):
    path = Path(current_app.root_path).parent / "content" / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _album_files(album):
    folder = Path(current_app.static_folder) / album
    if not folder.is_dir():
        return []
    return sorted(f.name for f in folder.iterdir() if f.name.lower().endswith(IMAGE_SUFFIXES))


def seed_database():
    """匯入初始資料，回傳各類筆數。"""
    counts = {"sections": 0, "artworks": 0, "students": 0, "photos": 0}

    for s_index, section_data in enumerate(_load_json("artworks")):
        section = Section(name=section_data["name"], sort_order=s_index)
        db.session.add(section)
        counts["sections"] += 1
        for a_index, item in enumerate(section_data["items"]):
            db.session.add(Artwork(
                code=item["id"], section=section, sort_order=a_index,
                title=item["title"], artist=item["artist"], year=item["year"],
                location=item["location"], description=item["desc"], answer=item["answer"],
                image=item["img"], audio=item["audio"], student_name=item["student_name"],
            ))
            counts["artworks"] += 1

    for index, item in enumerate(_load_json("students")):
        db.session.add(Student(name=item["name"], quote=item["quote"],
                               image=f"students/{item['image']}", sort_order=index))
        counts["students"] += 1

    for album in ALBUMS:
        for index, filename in enumerate(_album_files(album)):
            db.session.add(Photo(album=album, path=f"{album}/{filename}", sort_order=index))
            counts["photos"] += 1

    db.session.commit()
    return counts


def _require_tables():
    """資料表還沒建立時，給出明確的下一步，而不是一大串 traceback。"""
    if not inspect(db.engine).has_table("alembic_version"):
        raise click.ClickException("資料庫還沒有資料表，請先執行：flask --app app db upgrade")


def register_commands(app):
    @app.cli.command("seed")
    @click.option("--reset", is_flag=True, help="先清空作品、分區、小尖兵與相簿資料")
    def seed(reset):
        """把現有的 JSON 與相簿照片匯入資料庫。"""
        _require_tables()
        if reset:
            for model in (Artwork, Section, Student, Photo):
                model.query.delete()
            db.session.commit()
        elif Section.query.first() or Student.query.first() or Photo.query.first():
            raise click.ClickException("資料庫已有資料；若要重新匯入請加 --reset")

        counts = seed_database()
        click.echo("匯入完成：{sections} 個分區、{artworks} 件作品、{students} 位小尖兵、{photos} 張照片".format(**counts))

    @app.cli.command("create-admin")
    @click.argument("username")
    @click.password_option(prompt="密碼", confirmation_prompt="再輸入一次")
    def create_admin(username, password):
        """建立管理員；帳號已存在則重設密碼。"""
        _require_tables()
        if len(password) < 8:
            raise click.ClickException("密碼至少 8 個字元")
        user = User.query.filter_by(username=username).first() or User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"管理員 {username} 已設定完成")
