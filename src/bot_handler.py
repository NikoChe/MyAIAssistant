from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from models import Client, Session
from core import db, app
from datetime import datetime

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

user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Бесплатная диагностика", callback_data="free")],
        [InlineKeyboardButton("💰 Платная консультация", callback_data="paid")],
        [InlineKeyboardButton("👑 VIP сопровождение", callback_data="vip")],
    ]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите тип сессии:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_session_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    session_type = query.data
    user_id = query.from_user.id

    context.user_data["session_type"] = session_type
    context.user_data["answers"] = []
    context.user_data["current_question"] = 0

    user_state[user_id] = "answering"

    intro = session_questions[session_type]["intro"]
    await query.message.reply_text(intro)

    first_question = session_questions[session_type]["questions"][0]
    await query.message.reply_text(first_question)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_state.get(user_id) != "answering":
        await update.message.reply_text("🐛 Пришло сообщение, но не поймали: " + update.message.text)
        return

    answer = update.message.text
    session_type = context.user_data.get("session_type")
    context.user_data["answers"].append(answer)
    current = context.user_data.get("current_question", 0) + 1
    context.user_data["current_question"] = current

    questions = session_questions[session_type]["questions"]
    if current < len(questions):
        await update.message.reply_text(questions[current])
    else:
        summary = "\n".join(f"▪️ {q}\n🔹 {a}" for q, a in zip(questions, context.user_data["answers"]))
        await update.message.reply_text("📝 Вот, что вы написали:\n" + summary)

        keyboard = [
            [
                InlineKeyboardButton("✅ Подтвердить", callback_data="confirm"),
                InlineKeyboardButton("🔄 Редактировать", callback_data="edit")
            ]
        ]
        await update.message.reply_text(
            "✅ Это ваш финальный запрос?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        user_state[user_id] = "confirming"

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session_type = context.user_data.get("session_type")

    if query.data == "edit":
        context.user_data["answers"] = []
        context.user_data["current_question"] = 0
        first_question = session_questions[session_type]["questions"][0]
        await query.message.reply_text("🔄 Ок, давайте пройдём заново.")
        await query.message.reply_text(first_question)
        user_state[user_id] = "answering"
        return

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

        await query.message.reply_text("✅ Запрос подтверждён и сохранён.")
        user_state[user_id] = None
