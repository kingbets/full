from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import json, os

# 🔐 خواندن bot_token از فایل config.json
with open("config.json", "r") as f:
    config = json.load(f)

bot_token = config["bot_token"]

broadcast_state = {}
settings = {"delay": 10, "max_per_day": 50}

# 📦 اگر فایل members_db.json نبود، بساز
if not os.path.exists("members_db.json"):
    with open("members_db.json", "w") as f:
        json.dump({"group_users": {}, "private_users": {"users": []}}, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 وضعیت جذب", callback_data='status')],
        [InlineKeyboardButton("📢 پیام همگانی", callback_data='broadcast')],
        [InlineKeyboardButton("➕ افزودن ممبر واقعی", callback_data='start_real')],
        [InlineKeyboardButton("👻 افزودن ممبر فیک", callback_data='start_fake')],
        [InlineKeyboardButton("♻️ بروزرسانی دیتا", callback_data='refresh')],
        [InlineKeyboardButton("🛠️ تنظیمات", callback_data='settings')],
        [InlineKeyboardButton("🗂️ دریافت بکاپ", callback_data='backup')],
        [InlineKeyboardButton("⛔️ توقف عملیات", callback_data='stop')]
    ]
    await update.message.reply_text('سلام! از منوی زیر انتخاب کن:', reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    await query.answer()
    data = query.data

    with open("members_db.json", "r") as f:
        members = json.load(f)
    total_group = sum(len(v) for v in members.get("group_users", {}).values())
    total_private = len(members.get("private_users", {}).get("users", []))
    total_all = total_group + total_private

    if data == "status" or data == "refresh":
        text = f"📊 وضعیت کلی:\n👥 گروه‌ها: {total_group}\n💬 پی‌وی‌ها: {total_private}\n📦 مجموع: {total_all}"
        await query.edit_message_text(text=text, reply_markup=query.message.reply_markup)
    elif data == "broadcast":
        broadcast_state[chat_id] = True
        await query.message.reply_text("لطفاً پیام مورد نظر را برای ارسال همگانی ارسال کنید.")
    elif data == "start_real":
        await query.edit_message_text("✅ افزودن ممبر واقعی آغاز شد. اجرای فایل add_multi.py لازم است.", reply_markup=query.message.reply_markup)
    elif data == "start_fake":
        await query.edit_message_text("✅ افزودن ممبر فیک آغاز شد. اجرای فایل add_fake_members.py لازم است.", reply_markup=query.message.reply_markup)
    elif data == "stop":
        await query.edit_message_text("⛔️ عملیات متوقف شد. برای قطع دستی، اسکریپت را متوقف کنید.", reply_markup=query.message.reply_markup)
    elif data == "settings":
        await query.message.reply_text(f"⚙️ تنظیمات فعلی:\n⏱️ فاصله اددها: {settings['delay']} ثانیه\n📉 سقف ادد روزانه: {settings['max_per_day']}")
    elif data == "backup":
        if os.path.exists("members_db.json"):
            await context.bot.send_document(chat_id, document=InputFile("members_db.json"))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    if broadcast_state.get(chat_id):
        broadcast_state[chat_id] = False
        message = update.message.text
        with open("members_db.json", "r") as f:
            members = json.load(f)
        users = set()
        for group in members.get("group_users", {}).values():
            users.update(group)
        users.update(members.get("private_users", {}).get("users", []))

        success, failed = 0, 0
        for user_id in users:
            try:
                # قبل از ارسال پیام جدید بررسی می‌کنیم که آیا پیام قبلی همان پیام است
                if update.message.text != message:
                    await context.bot.send_message(chat_id=int(user_id), text=message)
                    success += 1
            except Exception as e:
                failed += 1

        await update.message.reply_text(f"📢 پیام ارسال شد. موفق: {success} | ناموفق: {failed}")

# 🟢 ساخت اپلیکیشن تلگرام از config
app = ApplicationBuilder().token(bot_token).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.run_polling()
