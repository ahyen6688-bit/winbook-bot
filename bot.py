from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging, asyncio, nest_asyncio, os
from keep_alive import keep_alive

# =======================
# ⚙️ CẤU HÌNH
# =======================
TOKEN = os.getenv("BOT_TOKEN")
VIDEO_URL = "https://n.uguu.se/broKObtn.mp4"
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

# =======================
# 👋 CHÀO THÀNH VIÊN MỚI
# =======================
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        chat_id = update.message.chat_id

        keyboard = [
            [
                InlineKeyboardButton("🔰 LINK ĐĂNG KÝ", url="https://www.winbook1.com"),
                InlineKeyboardButton("💬 Live Chat", url="https://direct.lc.chat/19402567/")
            ],
            [
                InlineKeyboardButton("👩‍💼 TELE CS001", url="https://t.me/WinbookCSKH001"),
                InlineKeyboardButton("👨‍💼 TELE CS002", url="https://t.me/WinbookCSKH002")
            ],
            [
                InlineKeyboardButton("📢 Kênh Chính", url="https://t.me/WinbookEvent"),
                InlineKeyboardButton("💭 Nhóm Chat", url="https://t.me/winbook8888")
            ],
            [
                InlineKeyboardButton("🌐 FANPAGE CHÍNH", url="https://www.facebook.com/profile.php?id=100076695622884")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        caption = (
            f"🎉 Chào mừng {member.mention_html()} đến với Winbook!\n\n"
            f"🧡 Chúc bạn vui vẻ và may mắn trong nhóm nhé 🧡"
        )

        try:
            await context.bot.send_animation(
                chat_id=chat_id,
                animation=VIDEO_URL,
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=chat_id,
                text=caption,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
            logging.error(f"Lỗi gửi video: {e}")

# =======================
# 🚫 LỌC TIN NHẮN XẤU
# =======================
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text.lower()
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
    keyboard = [
        [
            InlineKeyboardButton("🔰 Đăng ký", url="https://www.winbook1.com"),
            InlineKeyboardButton("💬 Live Chat", url="https://direct.lc.chat/19366399/")
        ],
        [
            InlineKeyboardButton("👩‍💼 CSKH001", url="https://t.me/WinbookCSKH001"),
            InlineKeyboardButton("👨‍💼 CSKH002", url="https://t.me/WinbookCSKH002")
        ],
        [
            InlineKeyboardButton("📢 Kênh Chính", url="https://t.me/WinbookEvent"),
            InlineKeyboardButton("💭 Nhóm Chat", url="https://t.me/winbook8888")
        ],
        [
            InlineKeyboardButton("🌐 FANPAGE CHÍNH", url="https://www.facebook.com/profile.php?id=100076695622884")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🤖 Bot Winbook đang hoạt động 24/7!\n\n"
        "💚 Mọi thứ đã sẵn sàng!",
        reply_markup=reply_markup
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

# =======================
# MAIN
# =======================
if __name__ == "__main__":
    keep_alive()
    nest_asyncio.apply()
    asyncio.run(run_bot())
