import os
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()

telegram_app = ApplicationBuilder().token(TOKEN).build()

videos = {}

# -------- WELCOME MESSAGE --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "hiii im your lil video vault bot :3\n\n"
        "send me a video and me will turn it into a link ;3\n\n"
        "i upload it myself and everything hehe"
    )

# -------- VIDEO HANDLER --------
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    video = update.message.video or update.message.document

    if not video:
        return

    await update.message.reply_text("uploading your video... me is working ;3")

    file = await context.bot.get_file(video.file_id)

    video_id = str(uuid.uuid4())
    file_path = f"videos/{video_id}.mp4"

    os.makedirs("videos", exist_ok=True)
    await file.download_to_drive(file_path)

    videos[video_id] = file_path

    link = f"https://telegram-video-host-production.up.railway.app/video/{video_id}"

    await update.message.reply_text(
        f"doneee :3\n\n"
        f"your video link is:\n{link}\n\n"
        f"share it wisely ;3"
    )

# -------- REGISTER HANDLERS --------
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.ALL, handle_video))


# -------- START TELEGRAM APP --------
@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.start()


# -------- WEBHOOK ENDPOINT --------
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


# -------- VIDEO PAGE --------
@app.get("/video/{video_id}", response_class=HTMLResponse)
async def get_video(video_id: str):
    if video_id not in videos:
        return "video not found ;("

    return f"""
    <html>
        <body style="margin:0;background:black;">
            <video width="100%" controls autoplay>
                <source src="/file/{video_id}" type="video/mp4">
            </video>
        </body>
    </html>
    """


# -------- RAW FILE SERVE --------
@app.get("/file/{video_id}")
async def serve_file(video_id: str):
    if video_id not in videos:
        return "video not found ;("

    return FileResponse(videos[video_id])
