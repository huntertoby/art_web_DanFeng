"""後台路由。除了登入頁以外，全部需要登入；所有寫入動作都用 POST（含 CSRF token）。"""
from urllib.parse import urlsplit

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from ..extensions import db, login_manager
from ..models import ALBUMS, Artwork, Photo, Section, Student, User
from ..storage import delete_upload, save_upload
from . import bp
from .forms import ArtworkForm, LoginForm, PhotoUploadForm, SectionForm, StudentForm, uploaded_file


@bp.before_request
def require_login():
    if request.endpoint != "admin.login" and not current_user.is_authenticated:
        return login_manager.unauthorized()


def _safe_next_url(target):
    """只接受站內路徑，避免登入後被導到外部網站（open redirect）。"""
    if not target:
        return None
    parts = urlsplit(target)
    if parts.scheme or parts.netloc or not target.startswith("/") or target.startswith("//"):
        return None
    return target


def _get_or_404(model, item_id):
    item = db.session.get(model, item_id)
    if item is None:
        abort(404)
    return item


def _move(item, direction):
    """和上一筆／下一筆交換順序。"""
    model = type(item)
    siblings = item.sibling_query()
    if direction == "up":
        neighbor = siblings.filter(model.sort_order < item.sort_order).order_by(model.sort_order.desc()).first()
    elif direction == "down":
        neighbor = siblings.filter(model.sort_order > item.sort_order).order_by(model.sort_order.asc()).first()
    else:
        abort(400)
    if neighbor:
        item.sort_order, neighbor.sort_order = neighbor.sort_order, item.sort_order
        db.session.commit()


# ---------------------------------------------------------------- 登入

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(_safe_next_url(request.args.get("next")) or url_for("admin.dashboard"))
        flash("帳號或密碼錯誤", "error")
    return render_template("admin/login.html", form=form)


@bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    flash("已登出", "success")
    return redirect(url_for("admin.login"))


@bp.route("/")
def dashboard():
    stats = {
        "artworks": Artwork.query.count(),
        "unpublished": Artwork.query.filter_by(is_published=False).count(),
        "sections": Section.query.count(),
        "students": Student.query.count(),
        "photos": Photo.query.count(),
    }
    recent = Artwork.query.order_by(Artwork.updated_at.desc()).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats, recent=recent)


# ---------------------------------------------------------------- 作品

@bp.route("/artworks")
def artworks():
    sections = Section.query.order_by(Section.sort_order).all()
    return render_template("admin/artworks.html", sections=sections)


@bp.route("/artworks/new", methods=["GET", "POST"])
def artwork_new():
    return _artwork_form(Artwork(is_published=True))


@bp.route("/artworks/<int:artwork_id>/edit", methods=["GET", "POST"])
def artwork_edit(artwork_id):
    return _artwork_form(_get_or_404(Artwork, artwork_id))


def _artwork_form(artwork):
    is_new = artwork.id is None
    form = ArtworkForm(obj=artwork)
    form.section_id.choices = [(s.id, s.name) for s in Section.query.order_by(Section.sort_order)]
    if not form.section_id.choices:
        flash("請先建立至少一個分區", "error")
        return redirect(url_for("admin.sections"))
    if request.method == "GET" and is_new:
        form.section_id.data = int(request.args.get("section", form.section_id.choices[0][0]))

    if form.validate_on_submit():
        duplicate = Artwork.query.filter(Artwork.code == form.code.data, Artwork.id != artwork.id).first()
        if duplicate:
            form.code.errors.append(f"編號已被「{duplicate.title}」使用")
        new_image, new_audio = uploaded_file(form.image), uploaded_file(form.audio)
        if is_new and not new_image:
            form.image.errors.append("新作品必須上傳圖片")

        if not form.code.errors and not form.image.errors:
            old_files = []
            section_changed = artwork.section_id != form.section_id.data
            form.populate_obj(artwork)  # 只會填入一般欄位，檔案欄位在下面處理

            if new_image:
                old_files.append(artwork.image)
                artwork.image = save_upload(new_image, "artworks")
            if new_audio:
                old_files.append(artwork.audio)
                artwork.audio = save_upload(new_audio, "audio")
            elif form.remove_audio.data:
                old_files.append(artwork.audio)
                artwork.audio = ""
            if section_changed:
                artwork.sort_order = artwork.next_sort_order()

            db.session.add(artwork)
            db.session.commit()
            for path in old_files:
                delete_upload(path)

            flash(f"已{'新增' if is_new else '更新'}「{artwork.title}」", "success")
            return redirect(url_for("admin.artworks", _anchor=f"section-{artwork.section_id}"))

    return render_template("admin/artwork_form.html", form=form, artwork=artwork, is_new=is_new)


@bp.route("/artworks/<int:artwork_id>/toggle", methods=["POST"])
def artwork_toggle(artwork_id):
    artwork = _get_or_404(Artwork, artwork_id)
    artwork.is_published = not artwork.is_published
    db.session.commit()
    flash(f"「{artwork.title}」已{'上架' if artwork.is_published else '下架'}", "success")
    return redirect(url_for("admin.artworks", _anchor=f"section-{artwork.section_id}"))


@bp.route("/artworks/<int:artwork_id>/move/<direction>", methods=["POST"])
def artwork_move(artwork_id, direction):
    artwork = _get_or_404(Artwork, artwork_id)
    _move(artwork, direction)
    return redirect(url_for("admin.artworks", _anchor=f"section-{artwork.section_id}"))


@bp.route("/artworks/<int:artwork_id>/delete", methods=["POST"])
def artwork_delete(artwork_id):
    artwork = _get_or_404(Artwork, artwork_id)
    files = [artwork.image, artwork.audio]
    db.session.delete(artwork)
    db.session.commit()
    for path in files:
        delete_upload(path)
    flash(f"已刪除「{artwork.title}」", "success")
    return redirect(url_for("admin.artworks"))


# ---------------------------------------------------------------- 分區

@bp.route("/sections", methods=["GET", "POST"])
def sections():
    form = SectionForm()
    if form.validate_on_submit():
        if Section.query.filter_by(name=form.name.data).first():
            form.name.errors.append("已有同名分區")
        else:
            section = Section(name=form.name.data)
            section.sort_order = section.next_sort_order()
            db.session.add(section)
            db.session.commit()
            flash(f"已新增分區「{section.name}」", "success")
            return redirect(url_for("admin.sections"))
    all_sections = Section.query.order_by(Section.sort_order).all()
    return render_template("admin/sections.html", form=form, sections=all_sections)


@bp.route("/sections/<int:section_id>/rename", methods=["POST"])
def section_rename(section_id):
    section = _get_or_404(Section, section_id)
    form = SectionForm()
    if not form.validate_on_submit():
        flash("分區名稱不可空白", "error")
    elif Section.query.filter(Section.name == form.name.data, Section.id != section.id).first():
        flash("已有同名分區", "error")
    else:
        section.name = form.name.data
        db.session.commit()
        flash("已更新分區名稱", "success")
    return redirect(url_for("admin.sections"))


@bp.route("/sections/<int:section_id>/move/<direction>", methods=["POST"])
def section_move(section_id, direction):
    _move(_get_or_404(Section, section_id), direction)
    return redirect(url_for("admin.sections"))


@bp.route("/sections/<int:section_id>/delete", methods=["POST"])
def section_delete(section_id):
    section = _get_or_404(Section, section_id)
    if section.artworks:
        flash(f"「{section.name}」裡還有 {len(section.artworks)} 件作品，請先移走或刪除", "error")
    else:
        db.session.delete(section)
        db.session.commit()
        flash(f"已刪除分區「{section.name}」", "success")
    return redirect(url_for("admin.sections"))


# ---------------------------------------------------------------- 藝術小尖兵

@bp.route("/students")
def students():
    return render_template("admin/students.html", students=Student.query.order_by(Student.sort_order).all())


@bp.route("/students/new", methods=["GET", "POST"])
def student_new():
    return _student_form(Student())


@bp.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
def student_edit(student_id):
    return _student_form(_get_or_404(Student, student_id))


def _student_form(student):
    is_new = student.id is None
    form = StudentForm(obj=student)
    if form.validate_on_submit():
        new_image = uploaded_file(form.image)
        if is_new and not new_image:
            form.image.errors.append("請上傳頭像")
        else:
            old_image = None
            student.name = form.name.data
            student.quote = form.quote.data
            if new_image:
                old_image = student.image
                student.image = save_upload(new_image, "students")
            if is_new:
                student.sort_order = student.next_sort_order()
            db.session.add(student)
            db.session.commit()
            delete_upload(old_image)
            flash(f"已{'新增' if is_new else '更新'}「{student.name}」", "success")
            return redirect(url_for("admin.students"))
    return render_template("admin/student_form.html", form=form, student=student, is_new=is_new)


@bp.route("/students/<int:student_id>/move/<direction>", methods=["POST"])
def student_move(student_id, direction):
    _move(_get_or_404(Student, student_id), direction)
    return redirect(url_for("admin.students"))


@bp.route("/students/<int:student_id>/delete", methods=["POST"])
def student_delete(student_id):
    student = _get_or_404(Student, student_id)
    db.session.delete(student)
    db.session.commit()
    delete_upload(student.image)
    flash(f"已刪除「{student.name}」", "success")
    return redirect(url_for("admin.students"))


# ---------------------------------------------------------------- 相簿

@bp.route("/photos")
def photos():
    counts = {album: Photo.query.filter_by(album=album).count() for album in ALBUMS}
    return render_template("admin/photos.html", albums=ALBUMS, counts=counts)


@bp.route("/photos/<album>", methods=["GET", "POST"])
def album(album):
    if album not in ALBUMS:
        abort(404)
    form = PhotoUploadForm()
    if form.validate_on_submit():
        next_order = Photo(album=album).next_sort_order()
        files = [f for f in form.photos.data if f and f.filename]
        for offset, file in enumerate(files):
            db.session.add(Photo(album=album, path=save_upload(file, f"photos/{album}"),
                                 sort_order=next_order + offset))
        db.session.commit()
        flash(f"已上傳 {len(files)} 張照片", "success")
        return redirect(url_for("admin.album", album=album))
    return render_template("admin/album.html", form=form, album=album, album_name=ALBUMS[album],
                           photos=Photo.in_album(album))


@bp.route("/photos/item/<int:photo_id>/move/<direction>", methods=["POST"])
def photo_move(photo_id, direction):
    photo = _get_or_404(Photo, photo_id)
    _move(photo, direction)
    return redirect(url_for("admin.album", album=photo.album, _anchor=f"photo-{photo.id}"))


@bp.route("/photos/item/<int:photo_id>/delete", methods=["POST"])
def photo_delete(photo_id):
    photo = _get_or_404(Photo, photo_id)
    db.session.delete(photo)
    db.session.commit()
    delete_upload(photo.path)
    flash("已刪除照片", "success")
    return redirect(url_for("admin.album", album=photo.album))
