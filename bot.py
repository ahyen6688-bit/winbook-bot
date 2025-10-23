from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import logging, nest_asyncio, asyncio
from keep_alive import keep_alive
from threading import Thread

# =======================
# ⚙️ CẤU HÌNH
# =======================
TOKEN = "8452228295:AAGk0BQqaRaqIw16BCL1jnZ0WL7OaoiUe5Q"
VIDEO_URL = "https://streamable.com/i5w6rq"
ADMIN_LINK = "https://t.me/Mikamika2111"
HOMEPAGE = "https://www.winbook1.com"

BAD_WORDS = [
    "đụ", "địt", "dm", "dcm", "mẹ mày", "ngu", "cc", "lồn",
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
logger = logging.getLogger(__name__)

# =======================
# 👋 TỰ ĐỘNG CHÀO THÀNH VIÊN MỚI
# =======================
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        for member in update.message.new_chat_members:
            chat_id = update.message.chat_id

            keyboard = [
                [
                    InlineKeyboardButton("🌐 Trang chủ", url=HOMEPAGE),
                    InlineKeyboardButton("👑 Admin", url=ADMIN_LINK)
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            text = (
                f"🎉 Chào mừng {member.mention_html()} đến với Winbook!\n\n"
                f"💚 Chúc bạn vui vẻ và may mắn trong nhóm nhé 💚"
            )

            # Gửi video chào (nếu link lỗi sẽ fallback sang text)
            try:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=VIDEO_URL,
                    caption=text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.warning(f"Không gửi được video: {e}")
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )

    except Exception as e:
        logger.error(f"Lỗi trong welcome(): {e}")

# =======================
# 🚫 LỌC TIN NHẮN BẬY
# =======================
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.message.from_user
    text = update.message.text.lower()
    chat_id = update.message.chat_id

    if any(bad_word in text for bad_word in BAD_WORDS):
        try:
            await update.message.delete()
        except:
            pass

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
                text=f"🚫 {user.mention_html()} đã bị kick do vi phạm 3 lần!",
                parse_mode="HTML"
            )
            try:
                await context.bot.ban_chat_member(chat_id, user_id)
            except Exception as e:
                logger.warning(f"Không thể kick: {e}")
            violation_count.pop(user_id, None)

# =======================
# 🚀 CHẠY BOT
# =======================
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

    print("🤖 Winbook Bot đang chạy 24/7...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

def main():
    keep_alive()
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(run_bot())

if __name__ == "__main__":
    main()
# =======================
# 🚀 KHỞI CHẠY BOT (ỔN ĐỊNH 24/7)
# =======================
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))
    app.add_handler(CommandHandler("start", start))  # /start riêng tư để test

    print("🤖 Winbook Bot đang chạy 24/7...")
    await app.run_polling()

def main():
    keep_alive()
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(run_bot())

if __name__ == "__main__":
    main()

