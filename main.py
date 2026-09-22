import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

# Bot tokenini kiriting
BOT_TOKEN = "8255212804:AAHjnqUqaumH8rbB2d-PM2eU4484XmQgJQ0"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 1. Boshlang'ich tugmalar (YouTube, Instagram va Keyingi sahifa)
main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔴 YouTube", 
                url="https://www.youtube.com/@AxeFamily1"
            ),
            InlineKeyboardButton(
                text="📸 Instagram", 
                url="https://www.instagram.com/axefamliy?utm_source=ig_web_button_share_sheet&stkn=ZDNlZDc0MzIxNw=="
            )
        ],
        [
            InlineKeyboardButton(
                text="➡️ Jamoaga qo'shilish", 
                callback_data="join_team"
            )
        ]
    ]
)

# 2. Orqaga qaytish tugmasi
back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⬅️ Orqaga qaytish", 
                callback_data="go_back"
            )
        ]
    ]
)

# /start komandasi uchun handler
@dp.message(CommandStart())
async def start_handler(message: Message):
    # Foydalanuvchining username yoki ismini olish
    user_name = message.from_user.username
    if user_name:
        display_name = f"@{user_name}"
    else:
        display_name = message.from_user.first_name

    text = f"Salom {display_name} AXEFAMLIY botiga xush kelibsiz!\n\nIjtimoiy tarmoqlarimiz:"
    
    await message.answer(text, reply_markup=main_keyboard)


# "Jamoaga qo'shilish" tugmasi bosilganda
@dp.callback_query(F.data == "join_team")
async def join_team_handler(callback: CallbackQuery):
    rules_text = (
        "AGAR JAMOAGA QO'SHILMOQCHI BO'LSANGIZ SHU SHARTLARGA ROZI BO'LING!\n\n"
        "• Telefoningiz 60FPS ko'tarsin\n"
        "• Gapira oling\n"
        "• Montaj qilishni biling\n"
        "• Sokinmang\n\n"
        "Xullas jamoaga qo'shilish uchun shartlar shu!"
    )
    
    # Xabarni o'zgartirish va orqaga qaytish tugmasini chiqarish
    await callback.message.edit_text(rules_text, reply_markup=back_keyboard)
    await callback.answer()


# "Orqaga qaytish" tugmasi bosilganda
@dp.callback_query(F.data == "go_back")
async def go_back_handler(callback: CallbackQuery):
    user_name = callback.from_user.username
    if user_name:
        display_name = f"@{user_name}"
    else:
        display_name = callback.from_user.first_name

    text = f"Salom {display_name} AXEFAMLIY botiga xush kelibsiz!\n\nIjtimoiy tarmoqlarimiz:"
    
    await callback.message.edit_text(text, reply_markup=main_keyboard)
    await callback.answer()


# Botni ishga tushirish
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
