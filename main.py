import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from googleapiclient.discovery import build
from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
from yt_dlp import YoutubeDL
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Telegram API məlumatları
API_KEY = 'AIzaSyAtmngrhhfmWL4_KvY1wUg3q4BXtUpNHAQ'
BOT_TOKEN = '5343918157:AAGbDSqpel-oOvthbkk-pWmu1gjgjKoTQJE'
API_ID = '17790748'
API_HASH = '6a387b92b75add555b30eb0045582f0e'
SESSION_STRING = '1AZWarzcBuxvBKhZqG9BycE2VUj3T4McWWipAhHscj7cbjAcTtRG2GUEfywh6MgiIT7SiJgL0SsQpr5Pzp1aS5vDUUr6TwC1wEWLq5wTfTioU6Jg-RMMOF1vpl0sXtq7qcDRdnnwz6QiZ1sXjcRefpav2MCIB40aJYYsob-u17ubfLrUYoJ-C6Wbd45WJ9_CZQdOyTGVWOQlFfAcCrgLq8hVj7isa2EdjwCHOcFYOXqBEqKT1H7zbCGLGnFUo76CdZLytgRIt-7ecSurhvHCksAEoKxLqUcSBGt64t0_-ZBJlOgf4DIGYih9l2CmQay0s-0kMLliOoYd6lhN0Ebo4gxi5NKDwIX4='

# YouTube servisini qurmaq
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Telegram userbot üçün Telethon client yaradılması
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

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

# Mahnı yükləmə funksiyası
def download_audio(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        return ydl.prepare_filename(info_dict)

# Telegram botu üçün start komandası
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Salam! Mahnı axtarmaq üçün '/axtar mahni adi' yazın.")

# Telegram botu üçün axtar komandası
async def axtar(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)  # Komandadan sonra verilən sözləri alır
    if not query:
        await update.message.reply_text("Xahiş edirəm mahnı adını daxil edin.")
        return

    await update.message.reply_text(f"Mahnı '{query}' axtarılır...")

    try:
        # YouTube-da mahnını tap
        video_id = search_youtube(query)
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        await update.message.reply_text(f"Mahnı tapıldı! İndi '/ses {video_url}' komutunu istifadə edərək musiqini oxutmaq üçün userbota göndərə bilərsiniz.")

    except Exception as e:
        await update.message.reply_text(f"Xəta baş verdi: {e}")

# Userbot üçün mesajları dinləyən handler
@client.on(events.NewMessage(pattern='/ses'))
async def handle_ses(event):
    message = event.message.message
    url = message.split(' ')[1]

    # Mahnını yüklə
    file_path = download_audio(url)

    # Sesli sohbete katıl ve müziği çal
    await client.join_voice_call(event.chat_id)
    voice_chat = client.voice_chat(event.chat_id)
    await voice_chat.play(file_path)

    # İşlem tamamlandığında sesli sohbetten ayrıl
    os.remove(file_path)
    await voice_chat.disconnect()

# Əsas funksiya
async def main():
    # Telegram botu yarat
    application = Application.builder().token(BOT_TOKEN).build()

    # Komandalar əlavə et
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("axtar", axtar))

    # Zamanlayıcı işlərini başlat
    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Baku'))
    scheduler.start()

    # Telegram botu başladın
    await application.run_polling()

if __name__ == '__main__':
    # Həm Telegram botu, həm də userbotu paralel olaraq işə sal
    loop = asyncio.get_event_loop()

    # Telegram botu işə salınır
    loop.create_task(main())

    # Userbotu işə salınır
    loop.create_task(client.start())

    # Loop-u işə salır
    loop.run_forever()
