import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# === MAP CHANNEL ===
CHANNELS = {
    "nocturne": {
        "name": "Nocturne",
        "id": -1002272523861  # Nocturne ✔️
    },
    "twotiger": {
        "name": "Two Tiger To Close",
        "id": -1001703082318  # Two Tiger To Close ✔️
    }
}

# === FILE HELPERS ===
def get_file(chat_id, file_type):
    return f"{file_type}_{chat_id}.txt"

def load_users(chat_id):
    try:
        with open(get_file(chat_id, "users"), "r") as f:
            return set(int(line.strip()) for line in f)
    except:
        return set()

def save_user(chat_id, user_id):
    with open(get_file(chat_id, "users"), "a") as f:
        f.write(f"{user_id}\n")

def save_declined(chat_id, user_id):
    with open(get_file(chat_id, "declined"), "a") as f:
        f.write(f"{user_id}\n")

# === AUTO FILTER ===
users_cache = {}

async def auto_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    chat_id = update.chat_join_request.chat.id
    user_id = user.id
    username = user.username

    if chat_id not in users_cache:
        users_cache[chat_id] = load_users(chat_id)

    users = users_cache[chat_id]

    if username is None:
        save_declined(chat_id, user_id)
        await context.bot.decline_chat_join_request(chat_id, user_id)
        print(f"{user.full_name} ditolak (no username)")
        return

    if user_id in users:
        save_declined(chat_id, user_id)
        await context.bot.decline_chat_join_request(chat_id, user_id)
        print(f"{user.full_name} ditolak (duplicate)")
        return

    users.add(user_id)
    await context.bot.approve_chat_join_request(chat_id, user_id)
    save_user(chat_id, user_id)
    print(f"{user.full_name} approved")

# === STATS ===
def count_lines(file):
    try:
        with open(file, "r") as f:
            return len(f.readlines())
    except:
        return 0

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Nocturne", callback_data="nocturne"),
            InlineKeyboardButton("Two Tiger To Close", callback_data="twotiger"),
        ]
    ]

    if update.message:
    await update.message.reply_text(
        "📊 Pilih channel:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# === BUTTON HANDLER ===
async def stats_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    key = query.data
    channel = CHANNELS.get(key)

    if not channel:
        return

    chat_id = channel["id"]

    approved = count_lines(get_file(chat_id, "users"))
    declined = count_lines(get_file(chat_id, "declined"))
    total = approved + declined

    text = (
        f"📊 {channel['name']}\n\n"
        f"✅ Approved: {approved}\n"
        f"🚫 Declined: {declined}\n"
        f"👥 Total: {total}"
    )

    await query.edit_message_text(text)

# === RUN ===
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(ChatJoinRequestHandler(auto_filter))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CallbackQueryHandler(stats_button))

print("Bot jalan... 💀")
app.run_polling()
