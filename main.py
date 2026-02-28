import os
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from telegram import Update, Bot
from telegram.ext import Dispatcher, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL")

bot = Bot(token=TOKEN)
app = FastAPI()

UPLOAD_FOLDER = "videos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

dispatcher = Dispatcher(bot=bot, update_queue=None, workers=0, use_context=True)

async def handle_video(update: Update, context):
    file = await bot.get_file(update.message.video.file_id)
    unique_name = str(uuid.uuid4()) + ".mp4"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    await file.download_to_drive(file_path)

    video_link = f"{BASE_URL}/video/{unique_name}"
    await bot.send_message(update.message.chat.id, f"Your video link:\n{video_link}")

dispatcher.add_handler(MessageHandler(filters.VIDEO, handle_video))

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return {"ok": True}

@app.get("/video/{filename}")
async def get_video(filename: str):
    return FileResponse(os.path.join(UPLOAD_FOLDER, filename))
