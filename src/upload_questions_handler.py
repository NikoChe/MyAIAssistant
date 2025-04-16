from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Document
from telegram.ext import ContextTypes, ConversationHandler
from notifier import is_owner
from core import app, db
from models import QuestionVersion, Question
import os, json
from datetime import datetime

UPLOAD_PATH = "/app/data/uploads/"
AWAIT_FILE, CONFIRM_UPLOAD = range(2)

# Команда /upload_questions
async def upload_questions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("⛔ У вас нет доступа.")
        return ConversationHandler.END

    await update.message.reply_text("📎 Отправьте .json файл со структурой вопросов.")
    return AWAIT_FILE

# Обработка загруженного файла
async def handle_uploaded_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc: Document = update.message.document
    user_id = update.effective_user.id

    if not doc.file_name.endswith(".json"):
        await update.message.reply_text("⚠️ Нужен файл формата .json")
        return ConversationHandler.END

    os.makedirs(UPLOAD_PATH, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(UPLOAD_PATH, f"version_import_{user_id}_{timestamp}.json")
    await doc.get_file().download_to_drive(file_path)

    context.user_data["uploaded_file_path"] = file_path
    await update.message.reply_text(
        f"✅ Файл получен. Нажмите кнопку, чтобы импортировать структуру.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 Импортировать", callback_data="confirm_import")]
        ])
    )
    return CONFIRM_UPLOAD

# Подтверждение импорта
async def confirm_import_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    file_path = context.user_data.get("uploaded_file_path")

    if not file_path or not os.path.exists(file_path):
        await query.message.reply_text("❌ Файл не найден. Попробуйте ещё раз.")
        return ConversationHandler.END

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        await query.message.reply_text("⚠️ Упс! Что-то пошло не так. Проверьте файл и загрузите заново.")
        return ConversationHandler.END

    # Проверка вложенности
    def depth_check(questions, parent_map=None, current_id=None, depth=0):
        if depth > 5:
            return False
        if not parent_map:
            parent_map = {q.get("id"): q.get("parent_id") for q in questions}
        children = [q.get("id") for q in questions if q.get("parent_id") == current_id]
        return all(depth_check(questions, parent_map, cid, depth + 1) for cid in children)

    if not depth_check(data):
        await query.message.reply_text("⚠️ Вопросы превышают допустимую вложенность (максимум 5 уровней). Импорт прерван.")
        return ConversationHandler.END

    # Импорт
    with app.app_context():
        version_id = "v" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
        version = QuestionVersion(id=version_id, owner_id=user_id, label="Импорт " + version_id)
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

    await query.message.reply_text(f"✅ Структура вопросов импортирована: <code>{version_id}</code>", parse_mode="HTML")
    return ConversationHandler.END
