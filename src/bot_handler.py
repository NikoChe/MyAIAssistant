from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

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

# user_id -> state
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
        await update.message.reply_text("✅ Это ваш финальный запрос?")
        user_state[user_id] = None
