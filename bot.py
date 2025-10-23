from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
from keep_alive import keep_alive

# ======================
# ⚙️ CẤU HÌNH
# ======================
VIDEO_URL = "https://streamable.com/i5w6rq"
ADMIN_LINK = "https://t.me/Mikamika2111"
HOMEPAGE = "https://www.winbook1.com"

TOKEN = os.getenv("BOT_TOKEN")

BAD_WORDS = [
    "đụ", "địt", "dm", "dmm", "dcm", "đm", "mẹ mày", "má mày", "ngu", "cc",
    "lồn", "sex", "sexy", "fuck", "bitch", "shit", "http", "https", "t.me", ".com"
]

violation_count = {}

# ======================
# 👋 CHÀO THÀNH VIÊN MỚI
# ======================
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"🎉 Chào mừng {member.mention_html()} đến với nhóm!\n"
            f"🌐 Trang chủ: {HOMEPAGE}\n📹 Video: {VIDEO_URL}\n👮‍♂️ Admin: {ADMIN_LINK}",
            parse_mode="HTML"
        )

# ======================
# 🚫 LỌC TỪ NGỮ XẤU
# ======================
async def filter_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.lower()

    if any(word in text for word in BAD_WORDS):
        await update.message.delete()
        violation_count[user.id] = violation_count.get(user.id, 0) + 1
        warns = violation_count[user.id]

        if warns < 3:
            await update.message.chat.send_message(
                f"⚠️ {user.mention_html()} đã vi phạm {warns}/3 lần. Cẩn thận nhé!",
                parse_mode="HTML"
            )
        else:
            await update.message.chat.ban_member(user.id)
            await update.message.chat.send_message(
                f"🚫 {user.mention_html()} đã bị kích khỏi nhóm do vi phạm quá 3 lần!",
                parse_mode="HTML"
            )

# ======================
# 🚀 KHỞI ĐỘNG BOT
# ======================
def main():
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_message))

    print("🤖 Winbook Bot đang chạy ổn định 24/7...")
    app.run_polling()

if __name__ == "__main__":
    main()
