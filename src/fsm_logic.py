from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from models import Client, Session, QuestionVersion, Question
from core import db, app
from notifier import notify_admins
from sqlalchemy import asc

SELECT_TYPE, ANSWERING, CONFIRMING = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    return await begin_session(update, context)

async def begin_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with app.app_context():
        version = QuestionVersion.query.filter_by(owner_id=user_id, active=True).first()
        if not version:
            await update.message.reply_text("👋 Добро пожаловать! Сейчас проверим, всё ли готово для начала работы...")
            await update.message.reply_text("❗️Не найдена активная структура вопросов. Используй /admin и /version_import")
            return ConversationHandler.END

        questions = Question.query.filter_by(version_id=version.id).order_by(asc(Question.order)).all()
        if not questions:
            await update.message.reply_text("👋 Добро пожаловать! Сейчас проверим, всё ли готово для начала работы...")
            await update.message.reply_text("❗️В версии нет ни одного вопроса.")
            return ConversationHandler.END

        context.user_data["questions"] = questions
        context.user_data["answers"] = []
        context.user_data["current"] = 0

    return await ask_next_question(update, context)

async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = context.user_data["current"]
    questions = context.user_data["questions"]

    if current >= len(questions):
        summary = "\n\n".join(
            f"❓ <b>{q.text}</b>\n🟢 {a}" for q, a in zip(questions, context.user_data["answers"])
        )
        await update.message.reply_text("📝 Вот, что вы написали:\n" + summary, parse_mode="HTML")

        keyboard = [[
            InlineKeyboardButton("✅ Подтвердить", callback_data="confirm"),
            InlineKeyboardButton("🔄 Редактировать", callback_data="edit")
        ]]
        await update.message.reply_text("✅ Это ваш финальный запрос?", reply_markup=InlineKeyboardMarkup(keyboard))
        return CONFIRMING

    question = questions[current]
    await update.message.reply_text(f"{question.text}")
    return ANSWERING

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["answers"].append(update.message.text)
    context.user_data["current"] += 1
    return await ask_next_question(update, context)

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "edit":
        context.user_data["answers"] = []
        context.user_data["current"] = 0
        await query.message.reply_text("🔄 Ок, давайте пройдём заново.")
        return await ask_next_question(query, context)

    if query.data == "confirm":
        user = query.from_user
        with app.app_context():
            client = Client.query.filter_by(telegram_id=user.id).first()
            if not client:
                client = Client(
                    telegram_id=user.id,
                    name=f"{user.first_name} {user.last_name or ''}".strip(),
                    initial_request=context.user_data["answers"][0],
                    username=user.username
                )
                db.session.add(client)
                db.session.commit()

            session = Session(
                client_id=client.id,
                session_type="default",
                answers_json={q.text: a for q, a in zip(context.user_data["questions"], context.user_data["answers"])},
                status="confirmed"
            )
            db.session.add(session)
            db.session.commit()

        await notify_admins(f"🆕 Новый запрос от {user.first_name} (@{user.username})")
        await query.message.reply_text("✅ Запрос подтверждён и сохранён.")
        return ConversationHandler.END
