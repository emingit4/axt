from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL
from pytgcalls import PyTgCalls
from telethon import TelegramClient
import asyncio
from pytgcalls.types import InputStream
from pytgcalls.types.stream import FileAudio

# Telegram API məlumatları
API_ID = '17790748'
API_HASH = '6a387b92b75add555b30eb0045582f0e'
BOT_TOKEN = '5343918157:AAGbDSqpel-oOvthbkk-pWmu1gjgjKoTQJE'

# YouTube API açarı
API_KEY = 'AIzaSyAtmngrhhfmWL4_KvY1wUg3q4BXtUpNHAQ'

# YouTube servisini qurmaq
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Telegram client və PyTgCalls qur
client = TelegramClient("userbot", API_ID, API_HASH)
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
    loop.run_until_complete(client.start())
    pytgcalls.start()

    # Botu başladın
    application.run_polling()

if __name__ == '__main__':
    main()
