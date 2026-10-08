import os
import logging
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from PIL import Image
import io

nest_asyncio.apply()

# جلب المفاتيح من متغيرات البيئة الأمانية
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

client = genai.Client(api_key=GEMINI_API_KEY)
user_sessions = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = client.chats.create(
        model="gemini-1.5-flash",
        config={"system_instruction": "أنت مساعد ذكي اسمك نوفا، يجيب باللغة العربية بأسلوب ودود وذكي."}
    )
    await update.message.reply_text("أهلاً بك! أنا نوفا. البوت يعمل الآن بشكل دائم 24/7!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    if user_id not in user_sessions:
        user_sessions[user_id] = client.chats.create(
            model="gemini-1.5-flash",
            config={"system_instruction": "أنت مساعد ذكي اسمك نوفا، يجيب باللغة العربية بأسلوب ودود وذكي."}
        )
    chat = user_sessions[user_id]
    response = chat.send_message(user_text)
    await update.message.reply_text(response.text)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("جاري تحليل الصورة...")
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    image = Image.open(io.BytesIO(photo_bytes))
    caption = update.message.caption or "اشرح لي هذه الصورة."
    response = client.models.generate_content(model="gemini-1.5-flash", contents=[image, caption])
    await update.message.reply_text(response.text)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling(drop_pending_updates=True)
