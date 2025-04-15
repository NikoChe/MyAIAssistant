from telegram import Update
from telegram.ext import ContextTypes
from models import QuestionVersion, Question
from core import app, db
from notifier import is_owner
import json
import os
from datetime import datetime

IMPORT_PATH = "/app/data/questions/default.json"
EXPORT_PATH = "/app/data/questions/export.json"

__all__ = ["admin_command", "version_export_command", "version_import_command"]

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("⛔ У вас нет доступа.")
        return
    await update.message.reply_text(
        "🛠 Вход в режим настройки.\n"
        "Варианты:\n"
        "1. /version_export — выгрузить текущую структуру вопросов\n"
        "2. /version_import — загрузить новую структуру из default.json"
    )

async def version_export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("⛔ У вас нет доступа.")
        return

    with app.app_context():
        version = QuestionVersion.query.filter_by(owner_id=user_id, active=True).first()
        if not version:
            await update.message.reply_text("❗️Нет активной версии.")
            return

        questions = Question.query.filter_by(version_id=version.id).order_by(Question.order).all()
        data = []
        for q in questions:
            data.append({
                "text": q.text,
                "type": q.type,
                "required": q.required,
                "options": q.options,
                "order": q.order,
                "parent_id": q.parent_id,
            })

        os.makedirs(os.path.dirname(EXPORT_PATH), exist_ok=True)
        with open(EXPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    await update.message.reply_text("✅ Структура вопросов экспортирована в export.json")

async def version_import_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("⛔ У вас нет доступа.")
        return

    if not os.path.exists(IMPORT_PATH):
        await update.message.reply_text("❗️Файл default.json не найден.")
        return

    with open(IMPORT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    with app.app_context():
        version_id = "v" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
        version = QuestionVersion(
            id=version_id,
            owner_id=user_id,
            label="Импорт " + version_id
        )
        db.session.add(version)
        db.session.flush()

        for i, q in enumerate(data):
            db.session.add(Question(
                version_id=version.id,
                text=q["text"],
                type=q.get("type", "text"),
                required=q.get("required", True),
                options=q.get("options"),
                order=q.get("order", i),
                parent_id=q.get("parent_id")
            ))

        QuestionVersion.query.filter_by(owner_id=user_id).update({QuestionVersion.active: False})
        version.active = True

        db.session.commit()

    await update.message.reply_text(f"✅ Загружена новая структура вопросов: <code>{version_id}</code>", parse_mode="HTML")
