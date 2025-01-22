import logging
from telethon.sessions import StringSession
from telethon import TelegramClient
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
import asyncio

# Logging konfiqurasiya
logging.basicConfig(level=logging.INFO)

# Telegram API məlumatları
API_ID = '17790748'
API_HASH = '6a387b92b75add555b30eb0045582f0e'
BOT_TOKEN = '5343918157:AAGbDSqpel-oOvthbkk-pWmu1gjgjKoTQJE'

# YouTube API açarı
API_KEY = 'AIzaSyAtmngrhhfmWL4_KvY1wUg3q4BXtUpNHAQ'

# YouTube servisini qurmaq
youtube = build('youtube', 'v3', developerKey=API_KEY)

# StringSession ilə sessiyanı daxil edirik
SESSION_STRING = '1AZWarzcBuxvBKhZqG9BycE2VUj3T4McWWipAhHscj7cbjAcTtRG2GUEfywh6MgiIT7SiJgL0SsQpr5Pzp1aS5vDUUr6TwC1wEWLq5wTfTioU6Jg-RMMOF1vpl0sXtq7qcDRdnnwz6QiZ1sXjcRefpav2MCIB40aJYYsob-u17ubfLrUYoJ-C6Wbd45WJ9_CZQdOyTGVWOQlFfAcCrgLq8hVj7isa2EdjwCHOcFYOXqBEqKT1H7zbCGLGnFUo76CdZLytgRIt-7ecSurhvHCksAEoKxLqUcSBGt64t0_-ZBJlOgf4DIGYih9l2CmQay0s-0kMLliOoYd6lhN0Ebo4gxi5NKDwIX4='

# Telegram client və PyTgCalls qur
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
pytgcalls = PyTgCalls(client)

# YouTube axtarış funksiyası
def search_youtube(query):
    request = youtube.search().list(
        part='snippet',
        q=query,
        type='video',
        maxResults=1
    )
    response = request.execute()
    return response['items'][0]['id']['videoId']

# Audio yükləmə funksiyası
def download_audio(video_id):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',  # Faylın adı və formatı
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        return ydl.prepare_filename(info_dict)

# Start komandası
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Salam! Mahnı axtarmaq üçün '/axtar mahni adi' yazın.")

# Mahnı axtarma komandası
async def axtar(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)  # Komandadan sonra verilən sözləri alır
    if not query:
        await update.message.reply_text("Xahiş edirəm mahnı adını daxil edin.")
        return

    await update.message.reply_text(f"Mahnı '{query}' axtarılır...")

    try:
        # YouTube-da mahnını tap
        video_id = search_youtube(query)
        await update.message.reply_text("Mahnı tapıldı! Yüklənir...")

        # Mahnını yüklə
        file_path = download_audio(video_id)

        # Telegram səsli söhbətdə oxumaq
        chat_id = update.effective_chat.id
        await pytgcalls.join_group_call(
            chat_id,
            MediaStream(
                file_path
            )
        )
        await update.message.reply_text("Mahnı səsli söhbətdə səsləndirilir!")

    except Exception as e:
        await update.message.reply_text(f"Xəta baş verdi: {e}")
        logging.error(f"Error in axtar command: {e}")

# Botu işə sal
async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Komanda və mesaj emalçılar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("axtar", axtar))  # /axtar komandasını əlavə et

    # Botu başladın
    await application.initialize()
    await application.start()

    # Tətbiqetmənin işini dayandırmaması üçün gözləyin
    await application.updater.start_polling()
    await application.updater.idle()

    await application.stop()
    await application.shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Error running the bot: {e}")
