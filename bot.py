from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging, os, asyncio
from keep_alive import keep_alive
from threading import Thread

# ======================
# ⚙️ CẤU HÌNH
# ======================
VIDEO_URL = "https://streamable.com/i5w6rq"
ADMIN_LINK = "https://t.me/Mikamika2111"
HOMEPAGE = "https://www.winbook1.com"
BANNER_URL = "https://i.postimg.cc/YqJt9y0C/winbook-banner.jpg"  # Thay bằng link banner của mày nha

TOKEN = os.getenv("BOT_TOKEN")

# Danh sách từ cấm
BAD_WORDS = [
    "đụ", "địt", "dm", "dmm", "dcm", "cc", "ngu", "má mày", "mẹ mày",
    "lồn", "sexy", "fuck", "bitch", "shit", "http", "https", ".com", "t.me"
]

# Bộ đếm cảnh cáo
violation_count = {}

# ======================
# 📜 LOGGING
# ======================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ======================
# 👋 CHÀO MỪNG THÀNH VIÊN MỚI
# ======================
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        try:
            chat_member = await context.bot.get_chat_member(update.effective_chat.id, context.bot.id)
            if chat_member.status not in ["administrator", "creator"]:
                print("⚠️ Bot chưa là admin, bỏ qua gửi tin chào.")
                return

            caption = (
                f"🎉 Chào mừng {member.mention_html()} đến với <b>Winbook!</b>\n"
                f"🍀 Chúc bạn vui vẻ & may mắn trong nhóm nhé!\n\n"
                f"🌐 <b>Trang chủ:</b> {HOMEPAGE}\n"
                f"🎬 <b>Video:</b> {VIDEO_URL}\n"
                f"👮‍♂️ <b>Admin:</b> {ADMIN_LINK}"
            )

            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=BANNER_URL,
                caption=caption,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Lỗi khi gửi chào mừng: {e}")

# ======================
# 🧹 LỌC TIN NHẮN BẬY, LINK, CHỬI THỀ
# ======================
async def filter_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id
    chat_id = message.chat_id
    text = message.text.lower() if message.text else ""

    # Kiểm tra bot có quyền admin không
    chat_member = await context.bot.get_chat_member(chat_id, context.bot.id)
    if chat_member.status not in ["administrator", "creator"]:
        return

    if any(word in text for word in BAD_WORDS):
        try:
            await message.delete()
        except:
            pass

        count = violation_count.get(user_id, 0) + 1
        violation_count[user_id] = count

        if count < 3:
            await message.chat.send_message(
                f"⚠️ <b>Cảnh cáo {count}/3:</b> {message.from_user.mention_html()} "
                f"vui lòng không gửi từ ngữ hoặc liên kết cấm!",
                parse_mode="HTML"
            )
        else:
            try:
                await message.chat.kick_member(user_id)
                await message.chat.send_message(
                    f"🚫 <b>{message.from_user.mention_html()}</b> đã bị kích khỏi nhóm do vi phạm quá 3 lần.",
                    parse_mode="HTML"
                )
                violation_count.pop(user_id, None)
            except Exception as e:
                print(f"Lỗi kick: {e}")

# ======================
# 🚀 LỆNH /START
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Xin chào {update.effective_user.mention_html()}!\n"
        f"Bot Winbook đang hoạt động 💪\n\n"
        f"📹 Video: {VIDEO_URL}\n"
        f"🌐 Trang chủ: {HOMEPAGE}\n"
        f"👮‍♂️ Admin: {ADMIN_LINK}",
        parse_mode="HTML"
    )

# ======================
# 🧠 MAIN
# ======================
def main():
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_message))

    print("🤖 Winbook Bot đang chạy ổn định 24/7...")
    app.run_polling()

if __name__ == "__main__":
    main()
