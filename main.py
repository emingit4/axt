from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from googleapiclient.discovery import build
from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
from yt_dlp import YoutubeDL
import asyncio

BOT_TOKEN = '5343918157:AAGbDSqpel-oOvthbkk-pWmu1gjgjKoTQJE'
API_ID = '17790748'
API_HASH = '6a387b92b75add555b30eb0045582f0e'
SESSION_STRING = '1AZWarzcBuxvBKhZqG9BycE2VUj3T4McWWipAhHscj7cbjAcTtRG2GUEfywh6MgiIT7SiJgL0SsQpr5Pzp1aS5vDUUr6TwC1wEWLq5wTfTioU6Jg-RMMOF1vpl0sXtq7qcDRdnnwz6QiZ1sXjcRefpav2MCIB40aJYYsob-u17ubfLrUYoJ-C6Wbd45WJ9_CZQdOyTGVWOQlFfAcCrgLq8hVj7isa2EdjwCHOcFYOXqBEqKT1H7zbCGLGnFUo76CdZLytgRIt-7ecSurhvHCksAEoKxLqUcSBGt64t0_-ZBJlOgf4DIGYih9l2CmQay0s-0kMLliOoYd6lhN0Ebo4gxi5NKDwIX4='

# Userbot qurulması
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Start komandası
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Salam! Mahnı axtarmaq üçün '/axtar mahni adi' yazın.")

# Mahnı axtarma komandası
async def axtar(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Xahiş edirəm mahnı adını daxil edin.")
        return

    await update.message.reply_text(f"Mahnı '{query}' axtarılır...")
    try:
        video_url = f"https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Placeholder link
        await update.message.reply_text(f"Mahnı tapıldı: {video_url}")
    except Exception as e:
        await update.message.reply_text(f"Xəta: {e}")

import asyncio

async def main():
    # Telegram botunun işlədilməsi
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("axtar", axtar))

    # Userbotun işlədilməsi
    await client.start()

    # Paralel olaraq bot və userbotu işə sal
    tasks = [
        application.run_polling(),
        client.run_until_disconnected(),
    ]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    # Mövcud döngədən istifadə et
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
