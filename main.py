import os
import uuid
from fastapi import FastAPI
from fastapi.responses import FileResponse
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL")

app = FastAPI()
UPLOAD_FOLDER = "videos"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

telegram_app = ApplicationBuilder().token(TOKEN).build()

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.video.get_file()
    unique_name = str(uuid.uuid4()) + ".mp4"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    await file.download_to_drive(file_path)

    video_link = f"{BASE_URL}/video/{unique_name}"
    await update.message.reply_text(f"Your video link:\n{video_link}")

telegram_app.add_handler(MessageHandler(filters.VIDEO, handle_video))

@app.get("/video/{filename}")
async def get_video(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    return FileResponse(file_path)

@app.on_event("startup")
async def start_bot():
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
