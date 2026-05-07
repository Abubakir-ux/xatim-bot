import asyncio
import logging
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BotCommand
from aiogram.exceptions import TelegramBadRequest
from aiogram.client.default import DefaultBotProperties

API_TOKEN = '8655041954:AAHs4kQitwIu0hnOblkyd9NM3bQSHPDoYO8'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()

xatm_db = {}

# Har bir juzning suralar diapazoni
JUZ_INFO = {
    1:  "Al-Fotiha 1 - Al-Baqara 141",
    2:  "Al-Baqara 142-252",
    3:  "Al-Baqara 253 - Ali Imron 92",
    4:  "Ali Imron 93 - An-Niso 23",
    5:  "An-Niso 24-147",
    6:  "An-Niso 148 - Al-Moida 81",
    7:  "Al-Moida 82 - Al-An'om 110",
    8:  "Al-An'om 111 - Al-A'rof 87",
    9:  "Al-A'rof 88 - Al-Anfol 40",
    10: "Al-Anfol 41 - At-Tavba 92",
    11: "At-Tavba 93 - Hud 5",
    12: "Hud 6 - Yusuf 52",
    13: "Yusuf 53 - Ibrohim 52",
    14: "Al-Hijr 1 - An-Nahl 128",
    15: "Al-Isro 1 - Al-Kahf 74",
    16: "Al-Kahf 75 - To-Ha 135",
    17: "Al-Anbiyo 1 - Al-Haj 78",
    18: "Al-Mo'minun 1 - Al-Furqon 20",
    19: "Al-Furqon 21 - An-Naml 55",
    20: "An-Naml 56 - Al-Ankabut 45",
    21: "Al-Ankabut 46 - Al-Ahzob 30",
    22: "Al-Ahzob 31 - Yo-Sin 27",
    23: "Yo-Sin 28 - Az-Zumar 31",
    24: "Az-Zumar 32 - Fussilat 46",
    25: "Fussilat 47 - Al-Josiya 37",
    26: "Al-Ahqof 1 - Az-Zariyot 30",
    27: "Az-Zariyot 31 - Al-Hadid 29",
    28: "Al-Mujodala 1 - At-Tahrim 12",
    29: "Al-Mulk 1 - Al-Mursalot 50",
    30: "An-Naba 1 - An-Nos 6",
}


def make_text(data):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    lines = [f"📖 <b>Xatim yaratildi!</b> | 🕐 {now}", ""]
    lines.append(f"👤 Yaratuvchi: {data['creator_username']}")
    lines.append("")
    if data["users"]:
        lines.append("📋 Qatnashuvchilar:")
        for i, name in enumerate(data["users"].values(), 1):
            lines.append(f"{i}. {name}")
    else:
        lines.append("📋 Qatnashuvchilar: hali yo'q")
    return "\n".join(lines)


def taqsimla(users, jami=30):
    n = len(users)
    if n == 0:
        return []
    names = list(users.values())
    if n >= jami:
        result = []
        for i, name in enumerate(names[:jami]):
            juz_num = i + 1
            result.append((name, 1, f"{juz_num}-juz", f"{JUZ_INFO[juz_num]}"))
        return result
    ulushlar = [1] * n
    for _ in range(jami - n):
        ulushlar[random.randint(0, n - 1)] += 1
    result = []
    current = 1
    for name, ulush in zip(names, ulushlar):
        if ulush == 1:
            juz_text = f"{current}-juz"
            sura_text = JUZ_INFO[current]
        else:
            juz_text = f"{current}-{current + ulush - 1} juzlar"
            sura_text = f"{JUZ_INFO[current].split(' - ')[0]} ... {JUZ_INFO[current + ulush - 1].split(' - ')[-1]}"
        result.append((name, ulush, juz_text, sura_text))
        current += ulush
    return result


def get_others(data):
    return [uid for uid in data["users"] if uid != data["creator_id"]]


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.type != "private":
        return
    bot_info = await bot.get_me()
    text = (
        "🕌 <b>Xatim.uz Botiga Xush Kelibsiz!</b>\n\n"
        "Bu bot guruhda <b>Xatim</b> tashkil qilishga yordam beradi.\n\n"
        "📌 <b>Qanday ishlaydi?</b>\n\n"
        "1️⃣ Botni guruhingizga qo'shing\n"
        "2️⃣ Guruhda <code>/xatimyaratish</code> buyrug'ini yozing\n"
        "3️⃣ Qatnashchilar <b>Qo'shilish</b> tugmasini bosadi\n"
        "4️⃣ Siz <b>Boshlash</b> tugmasini bosasiz\n"
        "5️⃣ Bot avtomatik <b>30 juzni</b> taqsimlaydi 📖\n\n"
        "👇 Botni guruhga qo'shish:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➕ Guruhga qo'shish", url=f"https://t.me/{bot_info.username}?startgroup=true")
    ]])
    await message.answer(text, reply_markup=kb)


@dp.message(Command("xatimyaratish"))
async def cmd_xatim(message: types.Message):
    user = message.from_user
    if not user:
        return

    creator_id = user.id
    creator_username = f"@{user.username}" if user.username else user.full_name

    data = {
        "creator_id": creator_id,
        "creator_username": creator_username,
        "users": {creator_id: creator_username},
        "chat_id": message.chat.id,
    }

    sent = await message.answer(make_text(data))
    xatm_db[sent.message_id] = data

    await sent.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➕ Qo'shilish", callback_data=f"join_{sent.message_id}")
    ]]))


@dp.callback_query(F.data.startswith("join_"))
async def cb_join(callback: CallbackQuery):
    msg_id = int(callback.data.split("_")[1])
    if msg_id not in xatm_db:
        return await callback.answer("Xatim topilmadi!", show_alert=True)

    data = xatm_db[msg_id]
    user_id = callback.from_user.id
    username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name

    if user_id == data["creator_id"]:
        return await callback.answer("Siz allaqachon ro'yxatdasiz! ✅", show_alert=False)

    if user_id in data["users"]:
        return await callback.answer("Allaqachon ro'yxatdasiz!", show_alert=False)

    data["users"][user_id] = username
    await callback.answer("Qo'shildingiz ✅")

    try:
        await callback.message.edit_text(
            make_text(data),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="⛔ Chiqish", callback_data=f"leave_{msg_id}")
            ]])
        )
    except TelegramBadRequest:
        pass

    if len(get_others(data)) >= 1:
        try:
            await bot.edit_message_reply_markup(
                chat_id=data["chat_id"],
                message_id=msg_id,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="📖 Boshlash", callback_data=f"boshlash_{msg_id}")
                ]])
            )
        except TelegramBadRequest:
            pass


@dp.callback_query(F.data.startswith("leave_"))
async def cb_leave(callback: CallbackQuery):
    msg_id = int(callback.data.split("_")[1])
    if msg_id not in xatm_db:
        return await callback.answer("Xatim topilmadi!", show_alert=True)

    data = xatm_db[msg_id]
    user_id = callback.from_user.id

    if user_id == data["creator_id"]:
        return await callback.answer()

    if user_id not in data["users"]:
        return await callback.answer("Siz ro'yxatda yo'qsiz!", show_alert=False)

    del data["users"][user_id]
    await callback.answer("Chiqdingiz ⛔")

    try:
        await callback.message.edit_text(
            make_text(data),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="➕ Qo'shilish", callback_data=f"join_{msg_id}")
            ]])
        )
    except TelegramBadRequest:
        pass

    if len(get_others(data)) == 0:
        try:
            await bot.edit_message_reply_markup(
                chat_id=data["chat_id"],
                message_id=msg_id,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="➕ Qo'shilish", callback_data=f"join_{msg_id}")
                ]])
            )
        except TelegramBadRequest:
            pass


@dp.callback_query(F.data.startswith("boshlash_"))
async def cb_boshlash(callback: CallbackQuery):
    msg_id = int(callback.data.split("_")[1])
    if msg_id not in xatm_db:
        return await callback.answer("Xatim topilmadi!", show_alert=True)

    data = xatm_db[msg_id]

    if callback.from_user.id != data["creator_id"]:
        return await callback.answer("Faqat yaratuvchi boshlaydi!", show_alert=True)

    taqsimlangan = taqsimla(data["users"], jami=30)
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    lines = [f"🕌 <b>Xatim boshlandi!</b> | 🕐 {now}", ""]
    lines.append(f"👥 Jami: {len(taqsimlangan)} kishi | 📖 30 juz\n")
    for name, ulush, juz_text, sura_text in taqsimlangan:
        lines.append(f"👤 {name}\n  📖 {juz_text}: {sura_text}\n")

    try:
        await callback.message.edit_text("\n".join(lines), reply_markup=None)
    except TelegramBadRequest:
        pass

    xatm_db.pop(msg_id, None)
    await callback.answer("Boshlandi! 📖")


async def main():
    await bot.set_my_commands([
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="xatimyaratish", description="Yangi xatim yaratish"),
    ])
    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())