import os
import uuid
import aiofiles
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import uvicorn
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL")

app = FastAPI()
UPLOAD_FOLDER = "videos"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/video/{filename}")
async def get_video(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    return FileResponse(file_path)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.video.get_file()
    unique_name = str(uuid.uuid4()) + ".mp4"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    await file.download_to_drive(file_path)

    video_link = f"{BASE_URL}/video/{unique_name}"
    await update.message.reply_text(f"Your video link:\n{video_link}")

async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
