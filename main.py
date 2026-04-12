import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

FILE_NAME = "users.txt"

# Load data
def load_users():
    try:
        with open(FILE_NAME, "r") as f:
            return set(int(line.strip()) for line in f)
    except:
        return set()

# Save user
def save_user(user_id):
    with open(FILE_NAME, "a") as f:
        f.write(f"{user_id}\n")

users = load_users()

# 🔥 HANDLE REQUEST
async def auto_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    chat_id = update.chat_join_request.chat.id
    user_id = user.id
    username = user.username

    # ❌ Tidak ada username
    if username is None:
        await context.bot.decline_chat_join_request(chat_id, user_id)
        print(f"{user.full_name} ditolak (tidak ada username)")
        return

    # ❌ Sudah pernah masuk
    if user_id in users:
        await context.bot.decline_chat_join_request(chat_id, user_id)
        print(f"{user.full_name} ditolak (sudah pernah masuk)")
        return

    # ✅ Approve
    users.add(user_id)
    save_user(user_id)
    await context.bot.approve_chat_join_request(chat_id, user_id)
    print(f"{user.full_name} di-approve (pertama kali)")


# 🚀 RUN
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(ChatJoinRequestHandler(auto_filter))

print("Bot jalan... 💀")
app.run_polling()
