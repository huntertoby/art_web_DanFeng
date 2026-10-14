# art_web — 丹鳳高中 114 學年度廣達「游於藝」義大利文藝復興展

Flask 網站，部署於 https://art-web-danfeng.onrender.com
前台展示作品、小尖兵與活動相簿；老師可從 `/admin` 後台管理所有內容。

## 專案結構

```
app.py                     入口（gunicorn app:app）
danfeng/
  __init__.py              create_app()：組裝設定、擴充套件、藍圖
  config.py                設定（DATABASE_URL、SECRET_KEY 由環境變數覆寫）
  models.py                資料表：Section、Artwork、Student、Photo、User
  public.py                前台路由（網址維持 .html 結尾，展場 QR Code 依賴它）
  admin/                   後台：routes.py（路由）、forms.py（表單與驗證）
  storage.py               上傳檔案的存放與刪除
  cli.py                   flask seed / flask create-admin 指令
templates/                 前台頁面；templates/admin/ 是後台
static/                    原始素材（作品圖、語音、相簿照片）、css、js
static/uploads/            後台上傳的檔案（不進 git）
content/*.json             初始資料，供 `flask seed` 匯入
migrations/                資料表版本（Flask-Migrate / Alembic）
docs/intents/              每個功能的意圖文件
tests/                     pytest
```

## 本機開發

```bash
pip install -r requirements-dev.txt

flask --app app db upgrade          # 建立資料表（預設 instance/site.db）
flask --app app seed                # 匯入 content/*.json 與 static/ 下的相簿照片
flask --app app create-admin admin  # 建立管理員，會提示輸入密碼（至少 8 字元）

python app.py                       # http://localhost:5000 ，後台在 /admin
pytest                              # 52 項測試
```

修改 `models.py` 之後：

```bash
flask --app app db migrate -m "說明這次改了什麼"
flask --app app db upgrade
```

## 部署到 Render

1. 建立 PostgreSQL 資料庫，把連線字串設為 Web Service 的環境變數 `DATABASE_URL`。
2. 設定環境變數 `SECRET_KEY`（一串夠長的亂數，例如 `python -c "import secrets; print(secrets.token_hex(32))"`）。
3. Build Command：`pip install -r requirements.txt && flask --app app db upgrade`
   Start Command：`gunicorn app:app`
4. 第一次部署後，在 Render 的 Shell 執行一次：
   `flask --app app seed` 和 `flask --app app create-admin 你的帳號`

⚠️ **上傳檔案的限制**：Render 免費方案的硬碟在每次重新部署時會被清空，
後台上傳的圖片／音檔（`static/uploads/`）會消失，但資料庫裡的紀錄還在。
正式使用前需擇一處理：掛載 Render Persistent Disk 到 `static/uploads`，或改寫 `danfeng/storage.py` 存到雲端儲存（S3、Cloudinary 等）。

## 常見維護

- **新增作品**：後台 →「作品」→「新增作品」。作品編號（如 `C-03`）就是展場 QR Code 的
  `/artworks.html?art=C-03`，改編號會讓舊的 QR Code 失效。
- **暫時不展示某件作品**：在作品列表點「已上架」切換成下架，不用刪除。
- **相簿**：後台 →「相簿」，可一次選多張上傳，用 ← → 調整順序。
