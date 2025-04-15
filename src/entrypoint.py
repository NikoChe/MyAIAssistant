import os
import logging
from threading import Thread
from fsm_logic import (
    start,
    handle_session_choice,
    handle_answer,
    handle_confirmation,
    SELECT_TYPE, ANSWERING, CONFIRMING
)
from admin_commands import sessions_command, set_bot_commands
from main import app  # Flask app с route из main.py

from telegram.ext import (
    ApplicationBuilder,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    Defaults
)

logging.basicConfig(level=logging.INFO)

telegram_app = (
    ApplicationBuilder()
    .token(os.getenv("TELEGRAM_BOT_TOKEN"))
    .defaults(Defaults(parse_mode="HTML"))
    .build()
)

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SELECT_TYPE: [CallbackQueryHandler(handle_session_choice)],
        ANSWERING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        CONFIRMING: [CallbackQueryHandler(handle_confirmation)],
    },
    fallbacks=[]
    # per_message=True  # ❌ Удалено, чтобы не было warning
)

telegram_app.add_handler(conv_handler)
telegram_app.add_handler(CommandHandler("sessions", sessions_command))

def run_flask():
    from werkzeug.serving import run_simple
    port = int(os.getenv("PORT", 6789))
    run_simple("0.0.0.0", port, app, use_reloader=False)

def main():
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(telegram_app.bot.delete_webhook(drop_pending_updates=True))
    logging.info("🧹 Webhook удалён")

    loop.run_until_complete(set_bot_commands(telegram_app.bot))  # ✅ меню команд

    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    telegram_app.run_polling()

if __name__ == "__main__":
    main()
