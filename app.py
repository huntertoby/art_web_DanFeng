"""入口檔。本機：python app.py；正式環境：gunicorn app:app"""
from danfeng import create_app
from danfeng.bootstrap import bootstrap, should_bootstrap

app = create_app()

# Render 上啟動時自動建表、匯入初始資料、建立管理員（見 danfeng/bootstrap.py）
if should_bootstrap():
    bootstrap(app)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
