import os
import logging
from threading import Thread
from main import app as flask_app
from main import telegram_app

logging.basicConfig(level=logging.INFO)
logging.info("🚀 Запуск Flask + Telegram (PTB 20.7)")

def run_flask():
    from werkzeug.serving import run_simple
    port = int(os.getenv("PORT", 6789))
    run_simple("0.0.0.0", port, flask_app, use_reloader=False)

def main():
    # Удаляем вебхук
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(telegram_app.bot.delete_webhook(drop_pending_updates=True))
    logging.info("🧹 Webhook удалён")

    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Запускаем Telegram
    telegram_app.run_polling()

if __name__ == "__main__":
    main()
