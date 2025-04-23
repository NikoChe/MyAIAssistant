import os
import logging
from flask import Flask
from threading import Thread
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    Defaults,
    ConversationHandler,
)
from fsm_logic import (
    start,
    handle_answer,
    handle_confirmation,
    SELECT_TYPE,
    ANSWERING,
    CONFIRMING,
)
from admin_commands import sessions_command, set_bot_commands
from admin_config_editor import admin_command, version_export_command, version_import_command
from upload_questions_handler import (
    upload_questions_command,
    handle_uploaded_file,
    confirm_import_callback,
    AWAIT_FILE,
    CONFIRM_UPLOAD,
)
from core import app

logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["GET"])
def index():
    return "✅ Flask работает!"

def run_flask():
    from werkzeug.serving import run_simple
    port = int(os.getenv("PORT", 6789))
    run_simple("0.0.0.0", port, app, use_reloader=False)

def main():
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    with app.app_context():
        telegram_app = (
            ApplicationBuilder()
            .token(os.getenv("TELEGRAM_BOT_TOKEN"))
            .defaults(Defaults(parse_mode="HTML"))
            .build()
        )

        telegram_app.add_handler(ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                ANSWERING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
                CONFIRMING: [CallbackQueryHandler(handle_confirmation)],
            },
            fallbacks=[]
        ))

        telegram_app.add_handler(ConversationHandler(
            entry_points=[CommandHandler("upload_questions", upload_questions_command)],
            states={
                AWAIT_FILE: [MessageHandler(filters.Document.ALL, handle_uploaded_file)],
                CONFIRM_UPLOAD: [CallbackQueryHandler(confirm_import_callback, pattern="^confirm_import$")],
            },
            fallbacks=[],
        ))

        telegram_app.add_handler(CommandHandler("sessions", sessions_command))
        telegram_app.add_handler(CommandHandler("admin", admin_command))
        telegram_app.add_handler(CommandHandler("version_export", version_export_command))
        telegram_app.add_handler(CommandHandler("version_import", version_import_command))

        loop.run_until_complete(telegram_app.bot.delete_webhook(drop_pending_updates=True))
        logging.info("🧹 Webhook удалён")

        loop.run_until_complete(set_bot_commands(telegram_app.bot))

        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()

        telegram_app.run_polling()

if __name__ == "__main__":
    main()
