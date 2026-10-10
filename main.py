import os
import asyncio
import time
from telethon import TelegramClient, events, Button
from pydub import AudioSegment

# Render uchun ffmpeg yo'lini ko'rsatish
AudioSegment.converter = "./ffmpeg"

# Sizning API ma'lumotlaringiz
API_ID = 33459811
API_HASH = '4ea33d6829d03d8293649aeb8db245d1'

# 1 minutlik limit uchun o'zgaruvchilar
last_sent_time = 0
LIMIT_SECONDS = 60

# Vaqtinchalik fayllarni saqlash uchun lug'at (user_id: file_path)
user_audio_cache = {}
# Foydalanuvchi tanlagan chatni vaqtinchalik saqlash
user_target_chat = {}

client = TelegramClient('user_session', API_ID, API_HASH)

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    if event.is_private:
        buttons = [
            [Button.inline("🎤 Voice yaratish", data="create_voice")]
        ]
        await event.respond(
            "Salom! Bu userbot orqali `.mp3` fayllaringizni istalgan guruh yoki shaxsiy chatga ovozli xabar (voice note) qilib yuborishingiz mumkin.\n\nBoshlash uchun pastdagi tugmani bosing:",
            buttons=buttons
        )

@client.on(events.CallbackQuery(data="create_voice"))
async def create_voice_callback(event):
    await event.edit("Menga `.mp3` formatdagi audio fayl yuboring!")

@client.on(events.NewMessage)
async def message_handler(event):
    global last_sent_time
    sender_id = event.sender_id

    if not event.is_private:
        return

    # 1. Agar foydalanuvchi MP3 fayl yuborsa
    if event.message.audio or event.message.voice or (event.message.document and event.message.file and event.message.file.name and event.message.file.name.endswith('.mp3')):
        status_msg = await event.reply("🔄 Audio yuklab olinmoqda...")
        input_file = f"input_{sender_id}.mp3"
        
        try:
            await event.message.download_media(file=input_file)
            user_audio_cache[sender_id] = input_file
            await status_msg.delete()

            # Guruhlarni skaner qilish
            dialogs_msg = await event.reply("🔍 Akkauntingizdagi guruhlar va chatlar skaner qilinmoqda...")
            buttons = []
            
            async for dialog in client.iter_dialogs(limit=30):
                # Guruhlar, superguruhlar va kanallar
                if dialog.is_group or dialog.is_channel:
                    buttons.append([Button.inline(f"👥 {dialog.name}", data=f"chat_{dialog.id}")])

            buttons.append([Button.inline("❌ Bekor qilish", data="cancel")])

            await dialogs_msg.edit(
                "✅ Audio qabul qilindi!\n\nOvozli xabar **qaysi guruhga** yuborilishini tanlang:\n*(Yoki shunchaki istalgan foydalanuvchining `@username` yoki chat ID sini yozib yuboring)*",
                buttons=buttons
            )
        except Exception as e:
            await status_msg.edit(f"❌ Xatolik yuz berdi: {str(e)}")

    # 2. Agar foydalanuvchi qo'lda username yoki chat ID yozsa (masalan: @username yoki -100...)
    elif sender_id in user_audio_cache and (event.message.text and not event.message.text.startswith('/')):
        target = event.message.text.strip()
        user_target_chat[sender_id] = target
        await process_and_send_voice(event, sender_id, target)

# Tugma orqali guruh tanlanganda
@client.on(events.CallbackQuery(pattern=r"chat_"))
async def chat_callback(event):
    sender_id = event.sender_id
    if sender_id not in user_audio_cache:
        await event.answer("Oldin MP3 fayl yuboring!", alert=True)
        return

    chat_id_str = event.data.decode().replace("chat_", "")
    target = int(chat_id_str)
    
    await event.edit("⏳ Ovozli xabar tayyorlanmoqda va yuborilmoqda...")
    await process_and_send_voice(event, sender_id, target, edit_message=True)

@client.on(events.CallbackQuery(data="cancel"))
async def cancel_callback(event):
    sender_id = event.sender_id
    if sender_id in user_audio_cache:
        if os.path.exists(user_audio_cache[sender_id]):
            os.remove(user_audio_cache[sender_id])
        del user_audio_cache[sender_id]
    if sender_id in user_target_chat:
        del user_target_chat[sender_id]
    await event.edit("❌ Amal bekor qilindi.")

# Ovozli xabarga o'tkazib yuborish funksiyasi
async def process_and_send_voice(event, sender_id, target, edit_message=False):
    global last_sent_time

    current_time = time.time()
    time_passed = current_time - last_sent_time

    if time_passed < LIMIT_SECONDS:
        remaining = int(LIMIT_SECONDS - time_passed)
        msg = f"⏳ **Limit tugamadi!** Iltimos, yana **{remaining} sekund** kuting."
        if edit_message:
            await event.edit(msg)
        else:
            await event.reply(msg)
        return

    input_file = user_audio_cache.get(sender_id)
    output_file = f"output_voice_{sender_id}.ogg"

    try:
        # MP3 ni OGG (Voice) formatiga o'tkazish
        audio = AudioSegment.from_file(input_file)
        audio.export(output_file, format="ogg", codec="libopus")

        # Akkauntingiz nomidan ovozli xabar yuborish
        await client.send_file(
            target,
            output_file,
            voice_note=True
        )

        last_sent_time = time.time()
        success_text = f"✅ Ovozli xabar **{target}** ga muvaffaqiyatli yuborildi!"
        
        if edit_message:
            await event.edit(success_text)
        else:
            await event.reply(success_text)

    except Exception as e:
        err_text = f"❌ Xatolik yuz berdi: {str(e)}"
        if edit_message:
            await event.edit(err_text)
        else:
            await event.reply(err_text)

    finally:
        # Fayllarni tozalash
        if input_file and os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)
        if sender_id in user_audio_cache:
            del user_audio_cache[sender_id]
        if sender_id in user_target_chat:
            del user_target_chat[sender_id]

async def main():
    print("Userbot ishga tushmoqda...")
    await client.start()
    print("Userbot muvaffaqiyatli ulandi va ishlamoqda!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
