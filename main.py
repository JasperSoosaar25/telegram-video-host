import os
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from telegram import Update, Bot
from telegram.ext import MessageHandler, filters, ContextTypes, Application

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL")

bot = Bot(token=BOT_TOKEN)
app = FastAPI()
UPLOAD_FOLDER = "videos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# This will handle videos
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.video.get_file()
    unique_name = str(uuid.uuid4()) + ".mp4"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    await file.download_to_drive(file_path)

    link = f"{BASE_URL}/video/{unique_name}"
    await bot.send_message(chat_id=update.effective_chat.id, text=f"Your video link:\n{link}")

# Set up handler
app_bot = Application.builder().token(BOT_TOKEN).build()
app_bot.add_handler(MessageHandler(filters.VIDEO, handle_video))

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await app_bot.process_update(update)
    return {"ok": True}

@app.get("/video/{filename}")
async def get_video(filename: str):
    return FileResponse(os.path.join(UPLOAD_FOLDER, filename))
