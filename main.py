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

# 💙 WELCOME MESSAGE
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "hiiii welcome to the cozy blue video vault :3\n\n"
        "send me a video and me will upload it safely and gently ;3\n\n"
        "me loves cyan things and videos"
    )

# 💙 REAL PROGRESS VIDEO HANDLER
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    video = update.message.video or update.message.document
    if not video:
        return

    file = await context.bot.get_file(video.file_id)

    video_id = str(uuid.uuid4())
    file_path = f"videos/{video_id}.mp4"
    os.makedirs("videos", exist_ok=True)

    status_message = await update.message.reply_text(
        "starting upload... me preparing softly ;3\n\n"
        "[⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜] 0%"
    )

    last_percent = -1

    async def progress(current, total):
        nonlocal last_percent

        percent = int(current * 100 / total)

        if percent != last_percent:
            last_percent = percent

            filled = percent // 10
            bar = "🟦" * filled + "⬜" * (10 - filled)

            try:
                await status_message.edit_text(
                    f"uploading your precious video... :3\n\n"
                    f"[{bar}] {percent}%\n\n"
                    f"me is carefully holding it in a cyan blanket ;3"
                )
            except:
                pass

    await file.download_to_drive(file_path, progress=progress)

    videos[video_id] = file_path

    link = f"https://telegram-video-host-production.up.railway.app/video/{video_id}"

    await status_message.edit_text(
        f"doneeeee :3\n\n"
        f"your cozy blue video link is:\n{link}\n\n"
        f"me kept it safe and warm ;3"
    )

# 💙 REGISTER HANDLERS
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.ALL, handle_video))

# 💙 START TELEGRAM
@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.start()

# 💙 WEBHOOK
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

# 💙 VIDEO PAGE (CYAN/BLUE THEME)
@app.get("/video/{video_id}", response_class=HTMLResponse)
async def get_video(video_id: str):
    if video_id not in videos:
        return "video not found ;("

    return f"""
    <html>
        <body style="margin:0;background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);color:white;display:flex;justify-content:center;align-items:center;height:100vh;">
            <video width="90%" controls autoplay style="border-radius:16px;box-shadow:0 0 40px rgba(0,255,255,0.4);">
                <source src="/file/{video_id}" type="video/mp4">
            </video>
        </body>
    </html>
    """

# 💙 RAW FILE SERVE
@app.get("/file/{video_id}")
async def serve_file(video_id: str):
    if video_id not in videos:
        return "video not found ;("

    return FileResponse(videos[video_id])
