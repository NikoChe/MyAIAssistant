import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    Defaults,
    ContextTypes
)

from bot_handler import start, handle_session_choice, handle_answer

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)
db = SQLAlchemy(app)

@app.route("/", methods=["GET"])
def index():
    return "✅ Flask работает!"

# === Telegram ===
telegram_app = (
    ApplicationBuilder()
    .token(os.getenv("TELEGRAM_BOT_TOKEN"))
    .defaults(Defaults(parse_mode="HTML"))
    .build()
)

# === Обработчики ===
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(handle_session_choice))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
