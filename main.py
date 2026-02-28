import os
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL")

app = FastAPI()
UPLOAD_FOLDER = "videos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.video.get_file()
    unique_name = str(uuid.uuid4()) + ".mp4"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    await file.download_to_drive(file_path)

    link = f"{BASE_URL}/video/{unique_name}"
    await update.message.reply_text(f"Your video link:\n{link}")

telegram_app.add_handler(MessageHandler(filters.VIDEO, handle_video))

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

@app.get("/video/{filename}")
async def get_video(filename: str):
    return FileResponse(os.path.join(UPLOAD_FOLDER, filename))
