import os
import logging
from flask import Flask
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    Defaults,
)

from bot_handler import (
    start,
    handle_session_choice,
    handle_answer,
    handle_confirmation,
)

from core import app  # ✅ импортируем ГОТОВЫЙ экземпляр app

logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["GET"])
def index():
    return "✅ Flask работает!"

# Telegram bot
telegram_app = (
    ApplicationBuilder()
    .token(os.getenv("TELEGRAM_BOT_TOKEN"))
    .defaults(Defaults(parse_mode="HTML"))
    .build()
)

# Хэндлеры
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(handle_session_choice, pattern="^(free|paid|vip)$"))
telegram_app.add_handler(CallbackQueryHandler(handle_confirmation, pattern="^(confirm|edit)$"))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
