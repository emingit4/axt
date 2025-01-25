from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from yt_dlp import YoutubeDL
from pytgcalls import PyTgCalls, idle
from telethon import TelegramClient
from pytgcalls.types import MediaStream

# Telegram bot tokeni və API məlumatları
BOT_TOKEN = '5343918157:AAGbDSqpel-oOvthbkk-pWmu1gjgjKoTQJE'
API_ID = '17790748'
API_HASH = '6a387b92b75add555b30eb0045582f0e'
SESSION_NAME = '1AZWarzcBuxvBKhZqG9BycE2VUj3T4McWWipAhHscj7cbjAcTtRG2GUEfywh6MgiIT7SiJgL0SsQpr5Pzp1aS5vDUUr6TwC1wEWLq5wTfTioU6Jg-RMMOF1vpl0sXtq7qcDRdnnwz6QiZ1sXjcRefpav2MCIB40aJYYsob-u17ubfLrUYoJ-C6Wbd45WJ9_CZQdOyTGVWOQlFfAcCrgLq8hVj7isa2EdjwCHOcFYOXqBEqKT1H7zbCGLGnFUo76CdZLytgRIt-7ecSurhvHCksAEoKxLqUcSBGt64t0_-ZBJlOgf4DIGYih9l2CmQay0s-0kMLliOoYd6lhN0Ebo4gxi5NKDwIX4='

# Audio yükləmə funksiyası
def download_audio(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',  # Ən yaxşı audio keyfiyyət
        'outtmpl': '%(title)s.%(ext)s',  # Faylın adı və formatı
        'cookiefile': 'cookies.txt',     # Cookies faylı
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',  # FFMPEG ilə audio çıxarır
                'preferredcodec': 'mp3',     # MP3 formatına çevirir
                'preferredquality': '192',   # Keyfiyyət (opsional)
            }
        ],
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        return ydl.prepare_filename(info_dict).replace('.webm', '.mp3')  # Fayl uzantısını düzəldir

# YouTube axtarış funksiyası
def search_youtube(query):
    ydl_opts = {
        'quiet': True,
        'cookiefile': 'cookies.txt',  # Cookies faylı
    }
    with YoutubeDL(ydl_opts) as ydl:
        search_results = ydl.extract_info(f"ytsearch:{query}", download=False)
        return search_results['entries'][0]['webpage_url']  # İlk nəticənin URL-si

# Start komandası
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Salam! Mahnı axtarmaq üçün '/axtar mahnı adı' yazın, mahnını oxumaq üçün isə '/oxu mahnı adı' yazın.")

# Səsli sohbətə qoşulma komandası
async def qosul(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Səsli sohbətə qoşulun...")
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)
    call = PyTgCalls(client)
    await call.start()
    await call.join_group_call(update.message.chat_id, MediaStream('silence.mp3'))  # Boş bir audio faylı çalır
    await idle()

# Mahnı oxuma komandası
async def oxu(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)  # Komandadan sonra yazılan sözləri alır
    if not query:
        await update.message.reply_text("Xahiş edirəm mahnı adını daxil edin.")
        return

    await update.message.reply_text(f"Mahnı '{query}' axtarılır...")

    try:
        video_url = search_youtube(query)  # YouTube-da mahnını tap
        await update.message.reply_text("Mahnı tapıldı! Yüklənir...")

        file_path = download_audio(video_url)  # Mahnını yüklə

        await update.message.reply_text("Mahnı yükləndi! Səsli söhbətdə oxunur...")

        client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        await client.start(bot_token=BOT_TOKEN)
        call = PyTgCalls(client)

        @call.on_stream_end()
        async def on_stream_end(_, update):
            await client.disconnect()

        await call.start()
        await call.join_group_call(update.message.chat_id, MediaStream(file_path))
        await idle()

    except Exception as e:
        await update.message.reply_text(f"Xəta baş verdi: {e}")

# Botu işə sal
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("qosul", qosul))  # /qosul komandasını əlavə edir
    application.add_handler(CommandHandler("oxu", oxu))  # /oxu komandasını əlavə edir

    application.run_polling()  # Botu başladır

if __name__ == '__main__':
    main()
