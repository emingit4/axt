from telethon.sessions import StringSession
from telethon import TelegramClient
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL
from pytgcalls import PyTgCalls
import asyncio
from pytgcalls.types import MediaStream, InputStream
from pytgcalls.types.input_stream import RemoteFile

# Telegram API məlumatları
API_ID = '17790748'
API_HASH = '6a387b92b75add555b30eb0045582f0e'
BOT_TOKEN = '5343918157:AAGbDSqpel-oOvthbkk-pWmu1gjgjKoTQJE'

# YouTube API açarı
API_KEY = 'AIzaSyAtmngrhhfmWL4_KvY1wUg3q4BXtUpNHAQ'

# YouTube servisini qurmaq
youtube = build('youtube', 'v3', developerKey=API_KEY)

# StringSession ilə sessiyanı daxil edirik
SESSION_STRING = 'AQEPdxwANek-BHKHo9gyfx1SC6Ly7OZmQYOhhbnMzANRVNn9qtk7SWB848fkXS5M0r3z-sPMZdEHhCqajUExfMFj7O6b1eqfO9eOI-GVMuw9QhRQ-DSuXLSkYPm9D-xJrywc69yfn2Ye1spd9JG99trjEXP8jtgIRWPVuMsn1o4B6aj0-CGvlXcpjkKheXcp55n55dANrHKbbDOn8XcokFbTAKAsY-efV4Fskyds6YLvPKUva7ZJT015y032RD9WKZySxI9NS4sgY6Va0-agu5fXAmdanNr4A2T72gj6rNfS9TKaDQy3oerz9VXupJQKdZkYKJpsQyEfonoxDcYDlt7w3su_UgAAAAE0nS3uAA'

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
            InputStream(
                RemoteFile(file_path)
            )
        )
        await update.message.reply_text("Mahnı səsli söhbətdə səsləndirilir!")

    except Exception as e:
        await update.message.reply_text(f"Xəta baş verdi: {e}")

# Botu işə sal
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Komanda və mesaj emalçılar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("axtar", axtar))  # /axtar komandasını əlavə et

    # PyTgCalls-u işə salmaq üçün event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.start())  # Burada session üçün `client.start()` çağırılır
    pytgcalls.start()

    # Botu başladın
    application.run_polling()

if __name__ == '__main__':
    main()
