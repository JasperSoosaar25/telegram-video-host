import os
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()

telegram_app = ApplicationBuilder().token(TOKEN).build()

videos = {}

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    if not video:
        return

    file = await context.bot.get_file(video.file_id)

    video_id = str(uuid.uuid4())
    file_path = f"videos/{video_id}.mp4"

    os.makedirs("videos", exist_ok=True)
    await file.download_to_drive(file_path)

    videos[video_id] = file_path

    link = f"https://telegram-video-host-production.up.railway.app/video/{video_id}"
    await update.message.reply_text(f"Your video link:\n{link}")

telegram_app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))


@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.start()


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


@app.get("/video/{video_id}", response_class=HTMLResponse)
async def get_video(video_id: str):
    if video_id not in videos:
        return "Video not found"

    return f"""
    <html>
        <body style="margin:0">
            <video width="100%" controls autoplay>
                <source src="/file/{video_id}" type="video/mp4">
            </video>
        </body>
    </html>
    """


@app.get("/file/{video_id}")
async def serve_file(video_id: str):
    from fastapi.responses import FileResponse

    if video_id not in videos:
        return "Video not found"

    return FileResponse(videos[video_id])
