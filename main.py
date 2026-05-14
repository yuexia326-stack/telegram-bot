import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ContextTypes, CommandHandler

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FILE_NAME = "users.txt"

def load_users():
    try:
        with open(FILE_NAME, "r") as f:
            return set(int(line.strip()) for line in f)
    except:
        return set()

def save_user(user_id):
    with open(FILE_NAME, "a") as f:
        f.write(f"{user_id}\n")

def save_declined(user_id):
    with open("declined.txt", "a") as f:
        f.write(f"{user_id}\n")

users = load_users()

async def auto_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    chat_id = update.chat_join_request.chat.id
    user_id = user.id
    username = user.username

    if username is None:
        save_declined(user_id)
        await context.bot.decline_chat_join_request(chat_id, user_id)
        print(f"{user.full_name} ditolak (tidak ada username)")
        return

    if user_id in users:
        save_declined(user_id)
        await context.bot.decline_chat_join_request(chat_id, user_id)
        print(f"{user.full_name} ditolak (sudah pernah masuk)")
        return

    users.add(user_id)
    await context.bot.approve_chat_join_request(chat_id, user_id)
    save_user(user_id)
    print(f"{user.full_name} di-approve (pertama kali)")

def count_lines(filename):
    try:
        with open(filename, "r") as f:
            return len(f.readlines())
    except:
        return 0

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    approved = count_lines("users.txt")
    declined = count_lines("declined.txt")
    total = approved + declined

    message = (
        "📊 Bot Stats\n\n"
        f"✅ Approved: {approved}\n"
        f"🚫 Declined: {declined}\n"
        f"👥 Total Requests: {total}"
    )

    await update.message.reply_text(message)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(ChatJoinRequestHandler(auto_filter))
app.add_handler(CommandHandler("stats", stats))  # ← INI TAMBAHAN

print("Bot jalan... 💀")
app.run_polling()

