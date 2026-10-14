"""入口檔。本機：python app.py；正式環境：gunicorn app:app"""
from danfeng import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
