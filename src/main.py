import os
import logging
from flask import Flask, request
from telegram import Bot
from telegram.error import TelegramError
from flask_sqlalchemy import SQLAlchemy

# === Логгирование ===
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

# === Flask + SQLAlchemy ===
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)
db = SQLAlchemy(app)

# === Telegram ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(text: str):
    if not TELEGRAM_TOKEN or not ADMIN_CHAT_ID:
        logging.warning("Telegram не настроен")
        return
    try:
        bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
        logging.info("Сообщение отправлено в Telegram")
    except TelegramError as e:
        logging.error(f"Ошибка Telegram: {e}")

# === Модель для теста ===
class Dummy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

# === Роуты ===
@app.route("/", methods=["GET"])
def index():
    try:
        db.create_all()
        logging.info("📦 Таблицы инициализированы")
    except Exception as e:
        logging.error(f"❌ Ошибка инициализации БД: {e}")
        send_telegram_message(f"❌ Ошибка инициализации БД:\n{e}")
    logging.info("GET / — проверка сервера")
    return "MyAIAssistant работает!"

# === Старт сервера ===
if __name__ == "__main__":
    logging.info("🚀 Сервер запущен на порту 6789")
    send_telegram_message("🚀 MyAIAssistant запущен и готов к работе!")
    app.run(host="0.0.0.0", port=6789)
