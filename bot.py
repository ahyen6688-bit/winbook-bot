from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging, asyncio, nest_asyncio, os
from keep_alive import keep_alive
from threading import Thread

# =======================
# ⚙️ CẤU HÌNH
# =======================
TOKEN = os.getenv("BOT_TOKEN")
VIDEO_URL = "https://streamable.com/i5w6rq"
ADMIN_LINK = "https://t.me/Mikamika2111"
HOMEPAGE = "https://www.winbook1.com"

BAD_WORDS = [
    "đụ", "địt", "dm", "dmm", "dcm", "mẹ mày", "má mày", "ngu", "cc", "lồn",
    "fuck", "bitch", "shit", "xxx", "sex", "http", "https", "t.me", ".com"
]

violation_count = {}

# =======================
# 🧠 LOGGING
# =======================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =======================
# 👋 CHÀO THÀNH VIÊN MỚI
# =======================
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        keyboard = [
            [
                InlineKeyboardButton("🌐 Trang chủ", url=HOMEPAGE),
                InlineKeyboardButton("👑 Admin", url=ADMIN_LINK)
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        caption = (
            f"🎉 Chào mừng {member.mention_html()} đến với Winbook!\n\n"
            f"💚 Chúc bạn vui vẻ và may mắn trong nhóm nhé 💚"
        )

        try:
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=VIDEO_URL,
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Lỗi gửi video: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=caption,
                parse_mode="HTML",
                reply_markup=reply_markup
            )

# =======================
# 🚫 LỌC TIN NHẮN XẤU
# =======================
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.message.from_user
    text = update.message.text.lower()
    chat_id = update.effective_chat.id

    if any(bad_word in text for bad_word in BAD_WORDS):
        await update.message.delete()
        user_id = user.id
        violation_count[user_id] = violation_count.get(user_id, 0) + 1
        count = violation_count[user_id]

        if count < 3:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ {user.mention_html()} vi phạm lần {count}/3. Cẩn thận kẻo bị kick!",
                parse_mode="HTML"
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🚫 {user.mention_html()} đã bị kick khỏi nhóm do vi phạm 3 lần!",
                parse_mode="HTML"
            )
            await context.bot.ban_chat_member(chat_id, user_id)
            violation_count.pop(user_id, None)

# =======================
# 🧩 LỆNH /START (chỉ để kiểm tra riêng)
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Winbook đang hoạt động ổn định 24/7 trên Render!\n"
        "Bạn có thể thêm bot vào nhóm để trải nghiệm tự động chào & quản lý tin nhắn 💚"
    )

# =======================
# 🚀 KHỞI CHẠY BOT
# =======================
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

    print("🤖 Winbook Bot đang chạy ổn định 24/7...")
    await app.run_polling()

def main():
    keep_alive()
    nest_asyncio.apply()
    asyncio.run(run_bot())

if __name__ == "__main__":
    Thread(target=main).start()
