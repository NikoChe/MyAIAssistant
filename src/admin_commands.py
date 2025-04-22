from telegram import Update, BotCommand
from telegram.ext import ContextTypes
from models import Client, Session
from core import app
from notifier import is_owner, is_manager
from datetime import datetime

__all__ = ["sessions_command", "set_bot_commands"]

async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not (is_owner(user_id) or is_manager(user_id)):
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return

    with app.app_context():
        sessions = Session.query.order_by(Session.created_at.desc()).limit(10).all()
        if not sessions:
            await update.message.reply_text("❗️Сессий пока нет.")
            return

        messages = []
        for s in sessions:
            client = Client.query.get(s.client_id)
            answers_formatted = "\n\n".join(
                f"❓ <b>{q}</b>\n🟢 {a}" for q, a in s.answers_json.items()
            )

            messages.append(
                f"👤 <b>{client.name}</b> (@{client.username})\n"
                f"🗂 Тип: <code>{s.session_type}</code>\n"
                f"📅 Время: <code>{s.created_at.strftime('%Y-%m-%d %H:%M')}</code>\n\n"
                f"{answers_formatted}"
            )

        await update.message.reply_text("\n\n".join(messages), parse_mode="HTML")


async def set_bot_commands(bot):
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("sessions", "Показать последние заявки (админ)"),
        BotCommand("admin", "Настроить структуру вопросов"),
        BotCommand("version_import", "Импорт структуры из default.json"),
        BotCommand("version_export", "Экспорт текущей структуры"),
        BotCommand("upload_questions", "Загрузить структуру вопросов (файл)")  # 🔥 добавлено
    ]
    await bot.set_my_commands(commands)
