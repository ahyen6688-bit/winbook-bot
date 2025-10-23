# bot.py
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive   # nếu mày có file keep_alive.py (Flask thread)
import asyncio

# ========== CẤU HÌNH ==========
VIDEO_URL = "https://streamable.com/i5w6rq"   # nếu link này dead -> thay bằng link mới
ADMIN_LINK = "https://t.me/Mikamika2111"
HOMEPAGE = "https://www.winbook1.com"

TOKEN = os.getenv("BOT_TOKEN")  # phải set trong Render environment

BAD_WORDS = [
    "đụ", "địt", "dm", "dcm", "mẹ mày", "ngu", "cc", "lồn",
    "fuck", "bitch", "shit", "xxx", "sex", "http", "https", "t.me", ".com"
]

violation_count = {}

# ========== LOGGING ==========
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ========== WELCOME (THÀNH VIÊN MỚI) ==========
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Gửi cho mỗi thành viên mới
    for member in update.message.new_chat_members:
        try:
            # Kiểm tra bot đã là admin chưa (nếu không có quyền gửi media trong nhóm thì sẽ fail)
            bot_member = await context.bot.get_chat_member(update.effective_chat.id, context.bot.id)
            if bot_member.status not in ("administrator", "creator"):
                # Nếu bot chưa là admin thì gửi text cảnh báo (hoặc ko gửi)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="⚠️ Bot cần quyền admin để gửi ảnh/video chào mừng. Vui lòng cấp quyền admin cho bot."
                )
                return

            # Keyboard buttons
            keyboard = [
                [
                    InlineKeyboardButton("🌐 Trang chủ", url=HOMEPAGE),
                    InlineKeyboardButton("🎬 Video", url=VIDEO_URL),
                ],
                [
                    InlineKeyboardButton("👮 Admin", url=ADMIN_LINK)
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Gửi video (nếu URL là video streamable/youtube it may be a link; Telegram sẽ preview)
            caption = (
                f"🎉 Chào mừng {member.mention_html()} đến với Winbook!\n\n"
                f"💚 Chúc bạn vui vẻ và may mắn trong nhóm nhé 💚"
            )

            # Thử gửi video (nếu streamable link hỗ trợ gửi, Telegram sẽ xử lý)
            try:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=VIDEO_URL,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            except Exception as e_video:
                # Nếu gửi video lỗi (ví dụ streamable dead), gửi ảnh (fallback)
                logger.warning(f"Send video failed: {e_video}. Sending a banner image fallback.")
                banner_img = "https://i.postimg.cc/YqJt9y0C/winbook-banner.jpg"  # thay bằng link hình thật của mày
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=banner_img,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )

        except Exception as e:
            logger.exception("Error in welcome handler: %s", e)


# ========== /start (gửi khi user private chat với bot) ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🌐 Trang chủ", url=HOMEPAGE),
            InlineKeyboardButton("🎬 Video", url=VIDEO_URL),
        ],
        [
            InlineKeyboardButton("👮 Admin", url=ADMIN_LINK)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = (
        f"👋 Xin chào {update.effective_user.mention_html()}!\n\n"
        f"🍀 <b>Bot Winbook</b> đang hoạt động 💪\n\n"
        f"🎉 Chúc bạn vui vẻ và may mắn trong nhóm!"
    )

    # cố gắng gửi video trước, fallback sang ảnh
    try:
        await update.message.reply_video(
            video=VIDEO_URL,
            caption=caption,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.warning("reply_video failed: %s. Using image fallback.", e)
        banner_img = "https://i.postimg.cc/YqJt9y0C/winbook-banner.jpg"
        await update.message.reply_photo(
            photo=banner_img,
            caption=caption,
            parse_mode="HTML",
            reply_markup=reply_markup
        )


# ========== FILTER TIN NHẮN XẤU ==========
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    chat_id = update.effective_chat.id
    user = update.message.from_user
    user_id = user.id

    # nếu phát hiện chuỗi chữ xấu (simple contains)
    if any(bad in text for bad in BAD_WORDS):
        try:
            await update.message.delete()
        except Exception:
            pass

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
                logger.warning("Không thể kick: %s", e)
            violation_count.pop(user_id, None)


# ========== MAIN ==========
def main():
    if not TOKEN:
        logger.error("BOT_TOKEN chưa được đặt trong environment variables.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

    # Nếu chạy trên Render: gọi keep_alive() để có webserver small (optional)
    try:
        keep_alive()
    except Exception:
        # nếu không có file keep_alive.py thì bỏ qua
        pass

    # ** Ghi nhớ: dùng run_polling() (không await) để tránh conflict với event loop **
    logger.info("🤖 Winbook Bot đang chạy... (polling)")
    app.run_polling()


if __name__ == "__main__":
    main()
