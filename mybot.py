import os
import asyncio
import time
from telethon import TelegramClient, events
from pydub import AudioSegment

# Sizning API ma'lumotlaringiz
API_ID = 33459811
API_HASH = '4ea33d6829d03d8293649aeb8db245d1'

# Xabar yuboriladigan bot
TARGET_CHAT = '@Ornimgayozibberuvchibot'

# 1 minutlik limit uchun o'zgaruvchilar
last_sent_time = 0
LIMIT_SECONDS = 60

# Telegram sessiyasini ochish
client = TelegramClient('user_session', API_ID, API_HASH)

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    if event.is_private:
        await event.respond(
            "Salom! Menga `.mp3` fayl yuboring, men uni 1 daqiqalik limit bilan "
            "@Ornimgayozibberuvchibot ga ovozli xabar qilib yuboraman."
        )

@client.on(events.NewMessage)
async def voice_sender(event):
    global last_sent_time

    # Faqat shaxsiy yozishmada va audio/dokument kelganda ishlaydi
    if event.is_private and (event.message.audio or event.message.voice or event.message.document):
        
        file_name = event.message.file.name if event.message.file else ""
        if not (event.message.audio or event.message.voice or file_name.endswith('.mp3')):
            return

        current_time = time.time()
        time_passed = current_time - last_sent_time

        # 1 minutlik limit tekshiruvi
        if time_passed < LIMIT_SECONDS:
            remaining = int(LIMIT_SECONDS - time_passed)
            await event.reply(f"⏳ **Limit tugamadi!** Iltimos, yana **{remaining} sekund** kuting.")
            return

        status_msg = await event.reply("🔄 Audio yuklanmoqda va ovozli xabarga o'tkazilmoqda...")

        input_file = "input_audio.mp3"
        output_file = "output_voice.ogg"

        try:
            # 1. MP3 faylni yuklab olish
            await event.message.download_media(file=input_file)

            # 2. OGG formatiga o'tkazish (Voice uchun)
            audio = AudioSegment.from_file(input_file)
            audio.export(output_file, format="ogg", codec="libopus")

            # 3. @Ornimgayozibberuvchibot ga ovozli xabar qilib yuborish
            await client.send_file(
                TARGET_CHAT,
                output_file,
                voice_note=True
            )

            # Vaqtni yangilash
            last_sent_time = time.time()
            await status_msg.edit(f"✅ Ovozli xabar **{TARGET_CHAT}** ga muvaffaqiyatli yuborildi!")

        except Exception as e:
            await status_msg.edit(f"❌ Xatolik yuz berdi: {str(e)}")

        finally:
            # Vaqtinchalik fayllarni tozalash
            if os.path.exists(input_file):
                os.remove(input_file)
            if os.path.exists(output_file):
                os.remove(output_file)

async def main():
    print("Userbot ishga tushmoqda...")
    await client.start()
    print("Userbot muvaffaqiyatli ulandi va ishlamoqda!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
