import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

# 🔥 ISI NANTI SETELAH DAPET ID
CHAT_IDS = []

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

users = load_users()

# 🔥 HANDLE REQUEST BARU
async def auto_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    chat_id = update.chat_join_request.chat.id
    user_id = user.id
    username = user.username

    # ❌ Tidak ada username
    if username is None:
        await context.bot.decline_chat_join_request(chat_id, user_id)
        print(f"{user.full_name} ditolak (tidak ada username)")
        print(chat_id)
        return

    # ❌ Sudah pernah masuk
    if user_id in users:
        await context.bot.decline_chat_join_request(chat_id, user_id)
        print(f"{user.full_name} ditolak (sudah pernah masuk)")
        print(chat_id)
        return

    # ✅ Approve
    users.add(user_id)
    save_user(user_id)
    await context.bot.approve_chat_join_request(chat_id, user_id)
    print(f"{user.full_name} di-approve (pertama kali)")
    print(chat_id)


# 🔥 HANDLE PENDING (AMAN, NGGAK ERROR WALAU KOSONG)
async def handle_pending(app):
    if not CHAT_IDS:
        print("CHAT_ID belum diisi")
        return

    for chat_id in CHAT_IDS:
        try:
            requests = await app.bot.get_chat_join_requests(chat_id)

            for req in requests:
                user = req.from_user
                user_id = user.id
                username = user.username

                if username is None:
                    await app.bot.decline_chat_join_request(chat_id, user_id)
                    print(f"{user.full_name} ditolak (pending)")
                    continue

                if user_id in users:
                    await app.bot.decline_chat_join_request(chat_id, user_id)
                    print(f"{user.full_name} ditolak (pending lama)")
                    continue

                users.add(user_id)
                save_user(user_id)
                await app.bot.approve_chat_join_request(chat_id, user_id)
                print(f"{user.full_name} di-approve (pending lama)")

        except Exception as e:
            print("Error:", e)


# 🚀 RUN
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(ChatJoinRequestHandler(auto_filter))
app.post_init = handle_pending

print("Bot jalan... 💀")
app.run_polling()
