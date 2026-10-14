"""上傳檔案的儲存。

檔案存在 static/uploads/<分類>/<隨機名稱>.<副檔名>，資料庫只記相對於 static/ 的路徑。
若之後要改存雲端（S3、Cloudinary…），只需要改這個檔案。
"""
import uuid
from pathlib import Path

from flask import current_app

UPLOAD_PREFIX = "uploads"
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
AUDIO_EXTENSIONS = {"mp3", "m4a", "wav", "ogg"}


def _extension(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def save_upload(file_storage, category):
    """存檔並回傳相對於 static/ 的路徑。檔名用 UUID，不沿用使用者的檔名。"""
    relative = f"{UPLOAD_PREFIX}/{category}/{uuid.uuid4().hex}.{_extension(file_storage.filename)}"
    target = Path(current_app.static_folder) / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    file_storage.save(target)
    return relative


def delete_upload(relative_path):
    """刪除後台上傳的檔案。原本就在 git 裡的素材（不在 uploads/ 底下）一律不動。"""
    if not relative_path or not relative_path.startswith(f"{UPLOAD_PREFIX}/"):
        return
    static_root = Path(current_app.static_folder).resolve()
    target = (static_root / relative_path).resolve()
    if static_root in target.parents and target.is_file():
        target.unlink()
