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

在 Render 上啟動時，`danfeng/bootstrap.py` 會自動：建立／更新資料表 → 資料庫為空時匯入初始資料 → 依環境變數建立管理員。
**不需要進 Shell 執行任何指令**（Render 免費方案也沒有 Shell）。

Web Service 的設定：

| 項目 | 值 |
|---|---|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| 環境變數 `SECRET_KEY` | 一串夠長的亂數：`python -c "import secrets; print(secrets.token_hex(32))"` |
| 環境變數 `ADMIN_USERNAME` | 後台帳號，例如 `admin` |
| 環境變數 `ADMIN_PASSWORD` | 後台密碼（至少 8 字元）；之後改這個值並重新部署即可改密碼 |
| 環境變數 `DATABASE_URL` | 選填，見下方 |

### 資料會不會保存？

- **沒設 `DATABASE_URL`**：使用 Render 硬碟上的 SQLite。Render 免費方案的硬碟在**每次部署或服務重啟時都會清空**，
  後台做的修改會消失，網站回到 `content/*.json` 的初始內容。前台展示不受影響，適合只想讓網站正常運作的情況。
- **要保存後台的修改**：建立一個 PostgreSQL（Render、Neon、Supabase 等都有免費方案，限制與期限請以各家最新說明為準），
  把連線字串設為 `DATABASE_URL`。第一次啟動會自動建表並匯入資料。
- 後台上傳的圖片／音檔存在 `static/uploads/`，同樣會在部署時被清空；要保存需掛載 Persistent Disk 或改寫 `danfeng/storage.py` 存到雲端。

## 常見維護

- **新增作品**：後台 →「作品」→「新增作品」。作品編號（如 `C-03`）就是展場 QR Code 的
  `/artworks.html?art=C-03`，改編號會讓舊的 QR Code 失效。
- **暫時不展示某件作品**：在作品列表點「已上架」切換成下架，不用刪除。
- **相簿**：後台 →「相簿」，可一次選多張上傳，用 ← → 調整順序。
