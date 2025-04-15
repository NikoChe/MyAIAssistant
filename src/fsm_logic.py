from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from models import Client, Session
from core import db, app
from notifier import notify_admins

SELECT_TYPE, ANSWERING, CONFIRMING = range(3)

session_questions = {
    "free": {
        "intro": "🔍 Бесплатная диагностическая сессия — это первая встреча, где мы разберем ваш запрос и посмотрим, как я могу помочь.",
        "questions": [
            "Какой ваш основной запрос. Что сейчас мешает или беспокоит?",
            "Как это мешает в жизни?",
            "Был ли опыт с другими специалистами, если да, то какой именно и каких целей достигли?"
        ]
    },
    "paid": {
        "intro": "💰 Платная консультация — полноценная сессия для проработки вашего запроса.",
        "questions": [
            "Какой ваш основной запрос на консультацию?",
            "Какой устойчивый результат планируете получить?",
            "Был ли опыт с другими специалистами, если да, то какой именно и каких целей достигли?"
        ]
    },
    "vip": {
        "intro": "👑 VIP сопровождение — индивидуальная работа с фокусом на результат и масштаб.",
        "questions": [
            "Какой ваш основной запрос на сопровождение?",
            "Какой устойчивый результат планируете получить?",
            "Был ли опыт с другими специалистами, если да, то какой именно и каких целей достигли?"
        ]
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Бесплатная диагностика", callback_data="free")],
        [InlineKeyboardButton("💰 Платная консультация", callback_data="paid")],
        [InlineKeyboardButton("👑 VIP сопровождение", callback_data="vip")],
    ]
    await update.message.reply_text(
        "Выберите тип сессии:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SELECT_TYPE

async def handle_session_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    session_type = query.data
    context.user_data["session_type"] = session_type
    context.user_data["answers"] = []
    context.user_data["current_question"] = 0

    intro = session_questions[session_type]["intro"]
    await query.message.reply_text(intro)
    await query.message.reply_text(session_questions[session_type]["questions"][0])
    return ANSWERING

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    session_type = context.user_data["session_type"]
    context.user_data["answers"].append(answer)

    current = context.user_data["current_question"] + 1
    context.user_data["current_question"] = current

    questions = session_questions[session_type]["questions"]
    if current < len(questions):
        await update.message.reply_text(questions[current])
        return ANSWERING

    summary = "\n".join(f"▪️ {q}\n🔹 {a}" for q, a in zip(questions, context.user_data["answers"]))
    await update.message.reply_text("📝 Вот, что вы написали:\n" + summary)

    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm"),
         InlineKeyboardButton("🔄 Редактировать", callback_data="edit")]
    ]
    await update.message.reply_text("✅ Это ваш финальный запрос?", reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRMING

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    session_type = context.user_data["session_type"]

    if query.data == "edit":
        context.user_data["answers"] = []
        context.user_data["current_question"] = 0
        await query.message.reply_text("🔄 Ок, давайте пройдём заново.")
        await query.message.reply_text(session_questions[session_type]["questions"][0])
        return ANSWERING

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
                session_type=session_type,
                answers_json={q: a for q, a in zip(session_questions[session_type]["questions"], context.user_data["answers"])},
                status="confirmed"
            )
            db.session.add(session)
            db.session.commit()

        await notify_admins(f"🆕 Новый запрос от {user.first_name} (@{user.username})")
        await query.message.reply_text("✅ Запрос подтверждён и сохранён.")
        return ConversationHandler.END
