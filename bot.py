from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging, asyncio, nest_asyncio, os
from keep_alive import keep_alive
from threading import Thread

# =======================
# ⚙️ CẤU HÌNH
# =======================
VIDEO_URL = "https://streamable.com/i5w6rq"
ADMIN_LINK = "https://t.me/Mikamika2111"
HOMEPAGE = "https://www.winbook1.com"

TOKEN = os.getenv("BOT_TOKEN")

BAD_WORDS = [
    "đụ", "địt", "dm", "dmm", "dcm", "đm", "mẹ mày", "má mày", "ngu", "cc", "lồn",
    "sex", "sexy", "fuck", "bitch", "shit", "http", "https", "t.me", ".com"
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
    member = update.message.new_chat_members[0]
    chat_id = update.message.chat_id

    keyboard = [
        [
            InlineKeyboardButton("🌐 Trang chủ", url=HOMEPAGE),
            InlineKeyboardButton("👑 Admin", url=ADMIN_LINK)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        f"🎉 Chào mừng {member.mention_html()} đến với <b>Winbook</b>!\n\n"
        f"💚 Chúc bạn vui vẻ và may mắn trong nhóm nhé 💚"
    )

    await context.bot.send_video(
        chat_id=chat_id,
        video=VIDEO_URL,
        caption=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# =======================
# 🚫 LỌC & XOÁ TIN NHẮN XẤU
# =======================
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text.lower() if update.message.text else ""
    chat_id = update.message.chat_id

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
                text=f"🚫 {user.mention_html()} đã bị kick do vi phạm 3 lần!",
                parse_mode="HTML"
            )
            await context.bot.ban_chat_member(chat_id, user_id)
            violation_count.pop(user_id, None)

# =======================
# 🧩 LỆNH /START
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Winbook Bot đang hoạt động 24/7!")

# =======================
# 🚀 KHỞI CHẠY BOT
# =====================
