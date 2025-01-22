from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import TelegramClient

# API açarı və bot tokeni
API_KEY = 'AIzaSyAtmngrhhfmWL4_KvY1wUg3q4BXtUpNHAQ'
BOT_TOKEN = '5343918157:AAGbDSqpel-oOvthbkk-pWmu1gjgjKoTQJE'

# Userbot üçün Telethon Client (String Session)
USERBOT_API_ID = '17790748'
USERBOT_API_HASH = '6a387b92b75add555b30eb0045582f0e'
USERBOT_SESSION_STRING = '1AZWarzcBuxvBKhZqG9BycE2VUj3T4McWWipAhHscj7cbjAcTtRG2GUEfywh6MgiIT7SiJgL0SsQpr5Pzp1aS5vDUUr6TwC1wEWLq5wTfTioU6Jg-RMMOF1vpl0sXtq7qcDRdnnwz6QiZ1sXjcRefpav2MCIB40aJYYsob-u17ubfLrUYoJ-C6Wbd45WJ9_CZQdOyTGVWOQlFfAcCrgLq8hVj7isa2EdjwCHOcFYOXqBEqKT1H7zbCGLGnFUo76CdZLytgRIt-7ecSurhvHCksAEoKxLqUcSBGt64t0_-ZBJlOgf4DIGYih9l2CmQay0s-0kMLliOoYd6lhN0Ebo4gxi5NKDwIX4='  # String session

# YouTube servisini qurmaq
youtube = build('youtube', 'v3', developerKey=API_KEY)

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

        # Faylı istifadəçiyə göndər
        with open(file_path, 'rb') as audio:
            await update.message.reply_audio(audio)

    except Exception as e:
        await update.message.reply_text(f"Xəta baş verdi: {e}")

# Botu işə sal
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Komanda və mesaj emalçılar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("axtar", axtar))  # /axtar komandasını əlavə et

    # Zamanlanmış işləri başlatmaq üçün `apscheduler` istifadə
    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Baku'))

    # Botu başladın
    application.run_polling()

    # Userbotu işə salmaq
    userbot = TelegramClient('userbot', USERBOT_API_ID, USERBOT_API_HASH)
    userbot.session = USERBOT_SESSION_STRING  # String session ilə əlaqə qururuq

    async def start_userbot():
        await userbot.start()
        print("Userbot işə düşdü!")

    with userbot:
        userbot.loop.run_until_complete(start_userbot())

if __name__ == '__main__':
    main()
