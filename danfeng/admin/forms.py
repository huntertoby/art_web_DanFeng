from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, MultipleFileField
from wtforms import BooleanField, PasswordField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp, ValidationError

from werkzeug.datastructures import FileStorage

from ..storage import AUDIO_EXTENSIONS, IMAGE_EXTENSIONS


def uploaded_file(field):
    """欄位裡真的有新上傳的檔案才回傳；用 obj= 建表單時 data 可能是舊路徑字串。"""
    data = field.data
    return data if isinstance(data, FileStorage) and data.filename else None

IMAGE_ONLY = FileAllowed(IMAGE_EXTENSIONS, "圖片只接受 " + "、".join(sorted(IMAGE_EXTENSIONS)))
AUDIO_ONLY = FileAllowed(AUDIO_EXTENSIONS, "音檔只接受 " + "、".join(sorted(AUDIO_EXTENSIONS)))


class LoginForm(FlaskForm):
    username = StringField("帳號", validators=[DataRequired()])
    password = PasswordField("密碼", validators=[DataRequired()])
    remember = BooleanField("記住我")


class SectionForm(FlaskForm):
    name = StringField("分區名稱", validators=[DataRequired(), Length(max=100)])


class ArtworkForm(FlaskForm):
    code = StringField("作品編號", validators=[
        DataRequired(), Length(max=20),
        Regexp(r"^[A-Za-z0-9-]+$", message="只能使用英文、數字和 -，例如 C-03"),
    ], description="展場 QR Code 用（/artworks.html?art=編號），不可重複")
    section_id = SelectField("分區", coerce=int)
    title = StringField("作品名稱", validators=[DataRequired(), Length(max=200)])
    artist = StringField("藝術家", validators=[Length(max=200)])
    year = StringField("年代", validators=[Length(max=50)])
    location = StringField("收藏地點", validators=[Length(max=200)])
    description = TextAreaField("作品賞析", validators=[DataRequired()])
    answer = TextAreaField("思考時刻（解答）", validators=[Optional()])
    student_name = StringField("語音導覽小尖兵", validators=[Length(max=50)])
    image = FileField("作品圖片", validators=[IMAGE_ONLY])
    audio = FileField("語音導覽", validators=[AUDIO_ONLY])
    remove_audio = BooleanField("移除目前的語音導覽")
    is_published = BooleanField("上架（顯示在前台）", default=True)

    FILE_FIELDS = ("image", "audio", "remove_audio")

    def populate_obj(self, obj):
        """只寫入一般欄位；檔案欄位由 view 另外處理（要存檔、刪舊檔）。"""
        for name, field in self._fields.items():
            if name not in self.FILE_FIELDS:
                field.populate_obj(obj, name)


class StudentForm(FlaskForm):
    name = StringField("姓名", validators=[DataRequired(), Length(max=50)])
    quote = TextAreaField("心得", validators=[DataRequired()])
    image = FileField("頭像", validators=[IMAGE_ONLY])


class PhotoUploadForm(FlaskForm):
    photos = MultipleFileField("選擇照片（可多選）")

    def validate_photos(self, field):
        files = [f for f in field.data if f and f.filename]
        if not files:
            raise ValidationError("請選擇至少一張照片")
        for f in files:
            if f.filename.rsplit(".", 1)[-1].lower() not in IMAGE_EXTENSIONS:
                raise ValidationError(f"{f.filename} 不是支援的圖片格式")
