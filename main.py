from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL
from pyrogram import Client
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
# API açarı və bot tokeni
API_KEY = 'AIzaSyAtmngrhhfmWL4_KvY1wUg3q4BXtUpNHAQ'
BOT_TOKEN = '5343918157:AAGbDSqpel-oOvthbkk-pWmu1gjgjKoTQJE'
SESSION_STRING = "1AZWarzcBuxvBKhZqG9BycE2VUj3T4McWWipAhHscj7cbjAcTtRG2GUEfywh6MgiIT7SiJgL0SsQpr5Pzp1aS5vDUUr6TwC1wEWLq5wTfTioU6Jg-RMMOF1vpl0sXtq7qcDRdnnwz6QiZ1sXjcRefpav2MCIB40aJYYsob-u17ubfLrUYoJ-C6Wbd45WJ9_CZQdOyTGVWOQlFfAcCrgLq8hVj7isa2EdjwCHOcFYOXqBEqKT1H7zbCGLGnFUo76CdZLytgRIt-7ecSurhvHCksAEoKxLqUcSBGt64t0_-ZBJlOgf4DIGYih9l2CmQay0s-0kMLliOoYd6lhN0Ebo4gxi5NKDwIX4="  # Buraya öz session stringinizi əlavə edin
API_ID = 17790748  # Telegram API ID (my.telegram.org-dan alınır)
API_HASH = "6a387b92b75add555b30eb0045582f0e"  # Telegram API HASH (my.telegram.org-dan alınır)

# YouTube servisini qur
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Userbot-u qur
userbot = Client(SESSION_STRING, api_id=API_ID, api_hash=API_HASH)

# YouTube axtarış funksiyası
def search_youtube(query):
    request = youtube.search().list(
        part='snippet',
        q=query,
        type='video',
        maxResults=1
    )
    response = request.execute()
    if response['items']:
        return response['items'][0]['id']['videoId']
    else:
        raise Exception("Mahnı tapılmadı.")

# Audio yükləmə funksiyası
def download_audio(video_id):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        return ydl.prepare_filename(info_dict)

# Telegram bot komandası: /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Salam! Mahnı axtarmaq üçün '/axtar mahni adi' yazın.")

# Telegram bot komandası: /axtar
async def axtar(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Xahiş edirəm mahnı adını daxil edin.")
        return

    await update.message.reply_text(f"Mahnı '{query}' axtarılır...")

    try:
        video_id = search_youtube(query)
        await update.message.reply_text("Mahnı tapıldı! Yüklənir...")
        file_path = download_audio(video_id)

        with open(file_path, 'rb') as audio:
            await update.message.reply_audio(audio)

    except Exception as e:
        await update.message.reply_text(f"Xəta baş verdi: {e}")

# Userbot mesaj idarəetməsi
@userbot.on_message()
async def userbot_handler(client, message):
    if "/axtar" in message.text:
        query = message.text.replace("/axtar", "").strip()
        if not query:
            await message.reply_text("Xahiş edirəm mahnı adını daxil edin.")
            return

        try:
            video_id = search_youtube(query)
            await message.reply_text("Mahnı tapıldı! Yüklənir...")
            file_path = download_audio(video_id)
            await client.send_audio(chat_id=message.chat.id, audio=file_path)
        except Exception as e:
            await message.reply_text(f"Xəta baş verdi: {e}")

# Bot və Userbot-u işlədən əsas funksiya
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Telegram bot komandaları
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("axtar", axtar))

    # Zamanlanmış işlər
    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Baku'))

    # Paralel olaraq Telegram botu və Userbot-u işə sal
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(application.run_polling()),
        loop.create_task(userbot.start())
    ]
    loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == '__main__':
    main()
