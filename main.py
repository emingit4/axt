from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from yt_dlp import YoutubeDL

# Telegram bot tokeni
BOT_TOKEN = '5343918157:AAGbDSqpel-oOvthbkk-pWmu1gjgjKoTQJE'

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
    await update.message.reply_text("Salam! Mahnı axtarmaq üçün '/axtar mahni adi' yazın.")

# Mahnı axtarma komandası
async def axtar(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)  # Komandadan sonra yazılan sözləri alır
    if not query:
        await update.message.reply_text("Xahiş edirəm mahnı adını daxil edin.")
        return

    await update.message.reply_text(f"Mahnı '{query}' axtarılır...")

    try:
        video_url = search_youtube(query)  # YouTube-da mahnını tap
        await update.message.reply_text("Mahnı tapıldı! Yüklənir...")

        file_path = download_audio(video_url)  # Mahnını yüklə

        with open(file_path, 'rb') as audio:
            await update.message.reply_audio(audio)  # Yüklənən faylı göndər

    except Exception as e:
        await update.message.reply_text(f"Xəta baş verdi: {e}")

# Botu işə sal
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("axtar", axtar))  # /axtar komandasını əlavə edir

    application.run_polling()  # Botu başladır

if __name__ == '__main__':
    main()
