import os, random
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler
)

USER_DATA = {}

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
print("BOT_TOKEN = ",BOT_TOKEN)

OPENINGS = {
  "sad": [
    "I’m really glad you reached out today.",
    "It sounds like today has been heavier than usual.",
    "Some days are harder to carry, and that’s okay."
  ],
  "unmotivated": [
    "Motivation doesn’t always show up on time.",
    "It’s okay to feel stuck sometimes."
  ]
}

REFLECTIONS = [
  "You’re working toward {goal} because {why}.",
  "This goal matters to you — {why}.",
  "You didn’t choose this path randomly. You chose it because {why}."
]

CLOSINGS = [
  "You don’t have to do everything today.",
  "One small step is enough for now.",
  "Rest if you need to, but don’t give up on yourself."
]


GOAL, WHY, MOOD = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi 👋 I’m your motivation companion.\n\n"
        "What is your main goal right now?"
    )
    return GOAL

async def receive_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["goal"] = update.message.text
    await update.message.reply_text("Why is this goal important to you?")
    return WHY

async def receive_why(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["why"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("😔 Sad", callback_data="sad")],
        [InlineKeyboardButton("😩 Unmotivated", callback_data="unmotivated")],
        [InlineKeyboardButton("😴 Tired", callback_data="tired")]
    ]

    await update.message.reply_text(
        "Thanks 💙 How are you feeling right now?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MOOD

async def mood_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    mood = query.data
    goal = context.user_data.get("goal")
    why = context.user_data.get("why")

    message = generate_motivation(mood, goal, why)
    await query.message.reply_text(message)

    return ConversationHandler.END

def generate_motivation(mood: str, goal: str, why: str):
    goal = goal or "something important to you"
    why = why or "a reason that matters to you"
    openings = OPENINGS.get(mood, [])
    opening = random.choice(openings) if openings else ""
    
    reflection_template = random.choice(REFLECTIONS)
    reflection = reflection_template.format(goal=goal, why=why)
    
    closing = random.choice(CLOSINGS)
    
    parts = [opening, reflection, closing]
    message = "\n\n".join(part for part in parts if part)
    
    return message

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_goal)],
        WHY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_why)],
        MOOD: [CallbackQueryHandler(mood_handler)]
    },
    fallbacks=[CommandHandler("start", start)],
    per_chat=True,
    per_user=True,
    per_message=False
)
 
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(conv_handler)
app.run_polling()