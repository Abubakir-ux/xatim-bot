import asyncio
import logging
import random
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BotCommand
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.client.default import DefaultBotProperties

API_TOKEN = '8655041954:AAF4QcY6UCqSWdkOsaCgrY_3l_anXs1o4R4'
SUPER_ADMIN_ID = 7480459140

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()

TARIX_FILE = "tarix.json"
USERS_FILE = "users.json"
STATS_FILE = "stats.json"

def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Saqlashda xato: {e}")

xatm_db = {}
tarix_db = load_json(TARIX_FILE)
stats_db = load_json(STATS_FILE)
users_db = load_json(USERS_FILE)

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
    uids = list(users.keys())
    names = list(users.values())
    if n >= jami:
        result = []
        for i in range(min(n, jami)):
            juz_num = i + 1
            result.append((uids[i], names[i], 1, f"{juz_num}-juz", JUZ_INFO[juz_num]))
        return result
    ulushlar = [1] * n
    for _ in range(jami - n):
        ulushlar[random.randint(0, n - 1)] += 1
    result = []
    current = 1
    for uid, name, ulush in zip(uids, names, ulushlar):
        if ulush == 1:
            juz_text = f"{current}-juz"
            sura_text = JUZ_INFO[current]
        else:
            juz_text = f"{current}-{current + ulush - 1} juzlar"
            sura_text = f"{JUZ_INFO[current].split(' - ')[0]} ... {JUZ_INFO[current + ulush - 1].split(' - ')[-1]}"
        result.append((uid, name, ulush, juz_text, sura_text))
        current += ulush
    return result


def get_others(data):
    return [uid for uid in data["users"] if uid != data["creator_id"]]


async def eslatma_yuborish(uid, name, juz_text, sura_text, chat_title, msg_id):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Ha, o'qidim!", callback_data=f"pm_tayyor_{msg_id}_{uid}"),
        InlineKeyboardButton(text="⏰ Keyinroq", callback_data=f"pm_keyin_{msg_id}_{uid}"),
    ]])
    text = (
        f"📖 <b>Xatim eslatmasi</b>\n\n"
        f"Siz <b>{chat_title}</b> guruhidagi xatimga qo'shilgansiz.\n\n"
        f"Sizga tegishli: <b>{juz_text}</b>\n"
        f"📌 {sura_text}\n\n"
        f"Juzingizni o'qidingizmi?"
    )
    try:
        await bot.send_message(chat_id=uid, text=text, reply_markup=kb)
        return True
    except (TelegramForbiddenError, Exception):
        return False


# ── /myid ──
@dp.message(Command("myid"))
async def cmd_myid(message: types.Message):
    await message.answer(f"🆔 Sizning ID ingiz: <code>{message.from_user.id}</code>")


# ── /start ──
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.type != "private":
        return
    bot_info = await bot.get_me()

    uid = str(message.from_user.id)
    uname = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    if uid not in users_db:
        users_db[uid] = {"ism": uname, "guruhlar": []}
    users_db[uid]["ism"] = uname
    save_json(USERS_FILE, users_db)

    text = (
        "🕌 <b>Xatim.uz Botiga Xush Kelibsiz!</b>\n\n"
        "Bu bot guruhda <b>Xatim</b> tashkil qilishga yordam beradi.\n\n"
        "📌 <b>Qanday ishlaydi?</b>\n\n"
        "1️⃣ Botni guruhingizga qo'shing va <b>Admin</b> qiling\n"
        "2️⃣ Guruhda <code>/xatimyaratish</code> yozing\n"
        "3️⃣ Qatnashchilar <b>Qo'shilish</b> tugmasini bosadi\n"
        "4️⃣ Siz <b>Boshlash</b> tugmasini bosasiz\n"
        "5️⃣ Bot 30 juzni avtomatik taqsimlaydi 📖\n"
        "6️⃣ Har bir qatnashchi o'z juzini o'qib <b>O'qidim</b> bosadi\n\n"
        "📊 <b>Buyruqlar:</b>\n"
        "<code>/xatimyaratish</code> — yangi xatim yaratish\n"
        "<code>/statistika</code> — shaxsiy statistika\n"
        "<code>/tarix</code> — guruh xatim tarixi\n"
        "<code>/reyting</code> — eng faol qatnashchilar\n\n"
        "⚠️ <b>Muhim:</b> Bot guruhda <b>Admin</b> bo'lishi kerak!\n\n"
        "👇 Botni guruhga qo'shish:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="➕ Guruhga qo'shish (Admin bilan)",
            url=f"https://t.me/{bot_info.username}?startgroup=true&admin=post_messages+delete_messages+restrict_members"
        )
    ]])
    await message.answer(text, reply_markup=kb)


# ── /xatimyaratish ──
@dp.message(Command("xatimyaratish"))
async def cmd_xatim(message: types.Message):
    if message.chat.type == "private":
        return await message.answer("Bu buyruq faqat guruhda ishlaydi!")
    user = message.from_user
    if not user:
        return

    try:
        bot_member = await bot.get_chat_member(message.chat.id, (await bot.get_me()).id)
        if bot_member.status not in ("administrator", "creator"):
            bot_info = await bot.get_me()
            kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="👑 Botni admin qilish",
                    url=f"https://t.me/{bot_info.username}?startgroup=true&admin=post_messages+delete_messages+restrict_members"
                )
            ]])
            return await message.answer(
                "⚠️ <b>Bot guruhda admin emas!</b>\n\n"
                "Iltimos, botni admin qiling!",
                reply_markup=kb
            )
    except:
        pass

    creator_id = user.id
    creator_username = f"@{user.username}" if user.username else user.full_name
    data = {
        "creator_id": creator_id,
        "creator_username": creator_username,
        "users": {creator_id: creator_username},
        "chat_id": message.chat.id,
        "chat_title": message.chat.title or "Guruh",
        "taqsim": [],
        "tayyor": [],
        "yaratilgan_vaqt": datetime.now().strftime("%d.%m.%Y %H:%M"),
    }
    sent = await message.answer(make_text(data))
    xatm_db[sent.message_id] = data
    await sent.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➕ Qo'shilish", callback_data=f"join_{sent.message_id}")
    ]]))

    chat_title = message.chat.title or "Guruh"
    chat_id_str = str(message.chat.id)
    chat_username = message.chat.username
    if chat_username:
        guruh_url = f"https://t.me/{chat_username}/{sent.message_id}"
    else:
        guruh_url = f"https://t.me/c/{str(message.chat.id)[4:]}/{sent.message_id}"

    elon_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="👥 Guruhga o'tish", url=guruh_url)
    ]])

    chat_id_variants = [chat_id_str, chat_id_str.replace("-100", "")]

    for uid_str, uinfo in users_db.items():
        try:
            uid_int = int(uid_str)
            if uid_int == creator_id:
                continue
            guruhlar = uinfo.get("guruhlar", [])
            if not any(g in guruhlar for g in chat_id_variants):
                continue
            await bot.send_message(
                chat_id=uid_int,
                text=f"📢 <b><a href='{guruh_url}'>{chat_title}</a></b> guruhida xatim yaratildi!\n\n"
                     f"👤 Yaratuvchi: {creator_username}\n\n"
                     f"Xatimga qo'shilasizmi?",
                reply_markup=elon_kb,
                disable_web_page_preview=True
            )
        except:
            pass


# ── Qo'shilish ──
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

    # Bu odamga Boshlash ko'rsatamiz (bosganida "Faqat yaratuvchi" deydi)
    try:
        await callback.message.edit_text(make_text(data), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📖 Boshlash", callback_data=f"boshlash_{msg_id}")
        ]]))
    except TelegramBadRequest:
        pass

    # Adminga ham Boshlash ko'rsatamiz
    if len(get_others(data)) >= 1:
        try:
            await bot.edit_message_reply_markup(
                chat_id=data["chat_id"], message_id=msg_id,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="📖 Boshlash", callback_data=f"boshlash_{msg_id}")
                ]])
            )
        except TelegramBadRequest:
            pass


# ── Chiqish ──
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

    # Bu odamga Qo'shilish qaytadi
    try:
        await callback.message.edit_text(make_text(data), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="➕ Qo'shilish", callback_data=f"join_{msg_id}")
        ]]))
    except TelegramBadRequest:
        pass

    # Hech kim qolmasa adminga ham Qo'shilish
    if len(get_others(data)) == 0:
        try:
            await bot.edit_message_reply_markup(
                chat_id=data["chat_id"], message_id=msg_id,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="➕ Qo'shilish", callback_data=f"join_{msg_id}")
                ]])
            )
        except TelegramBadRequest:
            pass


# ── Boshlash ──
@dp.callback_query(F.data.startswith("boshlash_"))
async def cb_boshlash(callback: CallbackQuery):
    msg_id = int(callback.data.split("_")[1])
    if msg_id not in xatm_db:
        return await callback.answer("Xatim topilmadi!", show_alert=True)
    data = xatm_db[msg_id]

    if callback.from_user.id != data["creator_id"]:
        return await callback.answer("Faqat yaratuvchi boshlaydi!", show_alert=True)

    taqsimlangan = taqsimla(data["users"], jami=30)
    data["taqsim"] = taqsimlangan
    data["tayyor"] = []
    jami = len(taqsimlangan)

    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    lines = [f"🕌 <b>Xatim boshlandi!</b> | 🕐 {now}", ""]
    lines.append(f"👥 Jami: {jami} kishi | 📖 30 juz\n")
    for uid, name, ulush, juz_text, sura_text in taqsimlangan:
        lines.append(f"👤 {name}\n  📖 {juz_text}: {sura_text}\n")

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=f"✅ O'qiganlar: 0/{jami}", callback_data=f"noop_{msg_id}")
    ]])

    try:
        await callback.message.edit_text("\n".join(lines), reply_markup=kb)
    except TelegramBadRequest:
        pass

    chat_id_str2 = str(data["chat_id"])
    for uid, name, ulush, juz_text, sura_text in taqsimlangan:
        uid_str = str(uid)
        if uid_str not in stats_db:
            stats_db[uid_str] = {"ism": name, "guruhlar": {}}
        stats_db[uid_str]["ism"] = name
        if "guruhlar" not in stats_db[uid_str]:
            stats_db[uid_str]["guruhlar"] = {}
        if chat_id_str2 not in stats_db[uid_str]["guruhlar"]:
            stats_db[uid_str]["guruhlar"][chat_id_str2] = {"jami_xatim": 0, "jami_juz": 0}
        stats_db[uid_str]["guruhlar"][chat_id_str2]["jami_xatim"] += 1
        stats_db[uid_str]["guruhlar"][chat_id_str2]["jami_juz"] += ulush
    save_json(STATS_FILE, stats_db)

    chat_id_str = str(data["chat_id"])
    if chat_id_str not in tarix_db:
        tarix_db[chat_id_str] = []
    tarix_db[chat_id_str].append({
        "vaqt": now,
        "yaratuvchi": data["creator_username"],
        "ishtirokchilar": jami,
    })
    tarix_db[chat_id_str] = tarix_db[chat_id_str][-50:]
    save_json(TARIX_FILE, tarix_db)

    chat_title = data.get("chat_title", "Guruh")
    yuborilamaganlar = []
    for uid, name, ulush, juz_text, sura_text in taqsimlangan:
        yuborildi = await eslatma_yuborish(uid, name, juz_text, sura_text, chat_title, msg_id)
        if not yuborildi:
            yuborilamaganlar.append(name)

    if yuborilamaganlar:
        ismlar = ", ".join(yuborilamaganlar)
        try:
            await bot.send_message(
                chat_id=data["chat_id"],
                text=f"⚠️ Quyidagilar botga <b>/start</b> yozmaganligi uchun eslatma yuborilamadi:\n{ismlar}\n\nIltimos, botga <b>/start</b> yozing!"
            )
        except:
            pass

    await callback.answer("Boshlandi! 📖")


# ── Tayyor (guruhda) ──
@dp.callback_query(F.data.startswith("tayyor_"))
async def cb_tayyor(callback: CallbackQuery):
    msg_id = int(callback.data.split("_")[1])
    if msg_id not in xatm_db:
        return await callback.answer("Xatim topilmadi!", show_alert=True)

    data = xatm_db[msg_id]
    user_id = callback.from_user.id
    taqsim_ids = [t[0] for t in data["taqsim"]]
    jami = len(data["taqsim"])

    if user_id not in taqsim_ids:
        return await callback.answer("Siz bu xatimda qatnashmayapsiz!", show_alert=True)
    if user_id in data["tayyor"]:
        return await callback.answer("Allaqachon belgilagansiz! ✅", show_alert=False)

    data["tayyor"].append(user_id)
    tayyor_soni = len(data["tayyor"])
    await callback.answer("Barakalloh! ✅", show_alert=True)

    try:
        current_text = callback.message.text or ""
        if "📊 O'qildi:" in current_text:
            current_text = current_text[:current_text.index("\n\n📊")]
        progress = f"\n\n📊 O'qildi: {tayyor_soni}/{jami} kishi"
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=f"✅ O'qiganlar: {tayyor_soni}/{jami}", callback_data=f"noop_{msg_id}")
        ]])
        await callback.message.edit_text(current_text + progress, reply_markup=kb)
    except TelegramBadRequest:
        pass

    if tayyor_soni == jami:
        await asyncio.sleep(1)
        try:
            await bot.send_message(
                chat_id=data["chat_id"],
                text=f"🎉 <b>Xatim yakunlandi!</b>\n\nBarcha {jami} kishi juzlarini o'qib bo'ldi!\nAlloh qabul qilsin! 🤲"
            )
        except:
            pass
        xatm_db.pop(msg_id, None)


# ── Tayyor (lichkadan) ──
@dp.callback_query(F.data.startswith("pm_tayyor_"))
async def cb_pm_tayyor(callback: CallbackQuery):
    parts = callback.data.split("_")
    msg_id = int(parts[2])
    uid = int(parts[3])

    if msg_id not in xatm_db:
        await callback.message.edit_text("✅ Javobingiz qabul qilindi! Alloh qabul qilsin! 🤲")
        return await callback.answer()

    data = xatm_db[msg_id]
    jami = len(data["taqsim"])

    if uid in data["tayyor"]:
        await callback.message.edit_text("✅ Siz allaqachon o'qib bo'lgansiz!")
        return await callback.answer()

    data["tayyor"].append(uid)
    tayyor_soni = len(data["tayyor"])

    await callback.message.edit_text(
        f"✅ <b>Barakalloh!</b>\n\nJuzingizni o'qib bo'ldingiz!\nAlloh qabul qilsin! 🤲\n\n"
        f"📊 Umumiy holat: {tayyor_soni}/{jami} kishi o'qib bo'ldi."
    )
    await callback.answer()

    try:
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=f"✅ O'qiganlar: {tayyor_soni}/{jami}", callback_data=f"noop_{msg_id}")
        ]])
        await bot.edit_message_reply_markup(
            chat_id=data["chat_id"], message_id=msg_id, reply_markup=kb
        )
    except:
        pass

    if tayyor_soni == jami:
        await asyncio.sleep(1)
        try:
            await bot.send_message(
                chat_id=data["chat_id"],
                text=f"🎉 <b>Xatim yakunlandi!</b>\n\nBarcha {jami} kishi juzlarini o'qib bo'ldi!\nAlloh qabul qilsin! 🤲"
            )
        except:
            pass
        xatm_db.pop(msg_id, None)


# ── Keyinroq ──
@dp.callback_query(F.data.startswith("pm_keyin_"))
async def cb_pm_keyin(callback: CallbackQuery):
    parts = callback.data.split("_")
    msg_id = int(parts[2])
    uid = int(parts[3])

    await callback.message.edit_text(
        "⏰ Xop, keyinroq o'qiysiz!\n\n3 soatdan keyin sizga yana eslatma yuboramiz."
    )
    await callback.answer("3 soatdan keyin eslatamiz! ⏰")

    # 3 soat kutib qayta eslatma yuboramiz
    asyncio.create_task(qayta_eslatma(uid, msg_id, callback.message))


async def qayta_eslatma(uid, msg_id, old_message):
    """3 soat kutib qayta eslatma yuborish"""
    await asyncio.sleep(3 * 60 * 60)  # 3 soat

    # Xatim hali davom etayaptimi?
    if msg_id not in xatm_db:
        return

    data = xatm_db[msg_id]

    # Odam allaqachon o'qib bo'ldimi?
    if uid in data["tayyor"]:
        return

    # Odam hali xatimda bormi?
    taqsim_ids = [t[0] for t in data["taqsim"]]
    if uid not in taqsim_ids:
        return

    # Uning juz ma'lumotini topamiz
    juz_text = ""
    sura_text = ""
    for t in data["taqsim"]:
        if t[0] == uid:
            juz_text = t[3]
            sura_text = t[4]
            break

    chat_title = data.get("chat_title", "Guruh")

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Ha, o'qidim!", callback_data=f"pm_tayyor_{msg_id}_{uid}"),
        InlineKeyboardButton(text="⏰ Keyinroq", callback_data=f"pm_keyin_{msg_id}_{uid}"),
    ]])

    try:
        await bot.send_message(
            chat_id=uid,
            text=f"🔔 <b>Eslatma!</b>\n\n"
                 f"<b>{chat_title}</b> guruhidagi xatimda sizga tegishli juz hali o'qilmagan.\n\n"
                 f"Sizga tegishli: <b>{juz_text}</b>\n"
                 f"📌 {sura_text}\n\n"
                 f"O'qib bo'ldingizmi?",
            reply_markup=kb
        )
    except:
        pass


# ── Noop ──
@dp.callback_query(F.data.startswith("noop_"))
async def cb_noop(callback: CallbackQuery):
    await callback.answer()


# ── /statistika ──
@dp.message(Command("statistika"))
async def cmd_statistika(message: types.Message):
    if message.chat.type == "private":
        return await message.answer("Bu buyruq faqat guruhda ishlaydi!")
    user_id = str(message.from_user.id)
    chat_id_str = str(message.chat.id)
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name

    s = stats_db.get(user_id, {})
    guruh_stats = s.get("guruhlar", {}).get(chat_id_str, {})

    if not guruh_stats or guruh_stats.get("jami_xatim", 0) == 0:
        await message.answer(
            f"📊 <b>{username} statistikasi</b>\n\n"
            f"Siz bu guruhda hali xatimda qatnashmadingiz.\n"
            f"/xatimyaratish bilan boshlang! 📖"
        )
        return

    await message.answer(
        f"📊 <b>{username} statistikasi</b>\n\n"
        f"📖 Bu guruhda xatimlarda qatnashgan: <b>{guruh_stats['jami_xatim']} marta</b>\n"
        f"📚 Jami o'qilgan juzlar: <b>{guruh_stats['jami_juz']} juz</b>\n\n"
        f"Alloh qabul qilsin! 🤲"
    )


# ── /tarix ──
@dp.message(Command("tarix"))
async def cmd_tarix(message: types.Message):
    if message.chat.type == "private":
        return await message.answer("Bu buyruq faqat guruhda ishlaydi!")
    chat_id_str = str(message.chat.id)

    if chat_id_str not in tarix_db or not tarix_db[chat_id_str]:
        await message.answer("📅 Bu guruhda hali xatim o'tkazilmagan.")
        return

    lines = ["📅 <b>Xatim tarixi (oxirgi 10 ta)</b>\n"]
    for i, x in enumerate(reversed(tarix_db[chat_id_str][-10:]), 1):
        lines.append(
            f"{i}. 🕐 {x['vaqt']}\n"
            f"   👤 Yaratuvchi: {x['yaratuvchi']}\n"
            f"   👥 Ishtirokchilar: {x['ishtirokchilar']} kishi\n"
        )
    await message.answer("\n".join(lines))


# ── /reyting ──
@dp.message(Command("reyting"))
async def cmd_reyting(message: types.Message):
    if message.chat.type == "private":
        return await message.answer("Bu buyruq faqat guruhda ishlaydi!")

    chat_id_str = str(message.chat.id)
    guruh_users = []
    for uid_str, s in stats_db.items():
        guruh_stats = s.get("guruhlar", {}).get(chat_id_str, {})
        if guruh_stats.get("jami_juz", 0) > 0:
            guruh_users.append({
                "ism": s["ism"],
                "jami_xatim": guruh_stats["jami_xatim"],
                "jami_juz": guruh_stats["jami_juz"],
            })

    if not guruh_users:
        await message.answer("🏆 Bu guruhda hali hech kim xatimda qatnashmagan.")
        return

    sorted_users = sorted(guruh_users, key=lambda x: x["jami_juz"], reverse=True)
    lines = ["🏆 <b>Eng faol qatnashchilar</b>\n"]
    medals = ["🥇", "🥈", "🥉"]

    for i, s in enumerate(sorted_users[:10], 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        lines.append(
            f"{medal} {s['ism']}\n"
            f"   📖 {s['jami_xatim']} xatim | 📚 {s['jami_juz']} juz\n"
        )
    await message.answer("\n".join(lines))


# ── /admin ──
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if not message.from_user:
        return

    # Guruhda — guruh admini uchun
    if message.chat.type in ("group", "supergroup"):
        try:
            member = await bot.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in ("administrator", "creator"):
                return await message.answer("❌ Bu buyruq faqat guruh adminlari uchun!")
        except:
            return

        chat_id_str = str(message.chat.id)

        # Guruh xatim soni
        g_xatim = sum(
            s.get("guruhlar", {}).get(chat_id_str, {}).get("jami_xatim", 0)
            for s in stats_db.values()
        )

        # Guruh qatnashchilar soni (unikal)
        qatnashchilar = set()
        for uid_str, s in stats_db.items():
            if s.get("guruhlar", {}).get(chat_id_str, {}).get("jami_xatim", 0) > 0:
                qatnashchilar.add(uid_str)

        # Guruh a'zolari soni (botga start bosganlar)
        azolar = sum(
            1 for u in users_db.values()
            if chat_id_str in u.get("guruhlar", [])
        )

        chat_title = message.chat.title or "Guruh"
        await message.answer(
            f"📊 <b>{chat_title} statistikasi</b>\n\n"
            f"📖 Jami xatimlar: <b>{g_xatim} ta</b>\n"
            f"👥 Jami qatnashchilar: <b>{len(qatnashchilar)} kishi</b>\n"
            f"👤 Botga ulangan azolar: <b>{azolar} kishi</b>"
        )
        return

    # Lichkada — faqat super admin uchun
    if message.from_user.id != SUPER_ADMIN_ID:
        return

    jami_user = len(users_db)

    # Guruhlar ro'yxati
    guruhlar = {}
    for uid_str, uinfo in users_db.items():
        for g_id in uinfo.get("guruhlar", []):
            if g_id not in guruhlar:
                guruhlar[g_id] = {"azolar": 0, "qoshgan": uid_str}
            guruhlar[g_id]["azolar"] += 1

    # Jami xatimlar
    jami_xatim = 0
    for s in stats_db.values():
        for g_stats in s.get("guruhlar", {}).values():
            jami_xatim += g_stats.get("jami_xatim", 0)

    faol_guruhlar = 0  # oldin hisoblaymiz
    guruh_lines = []  # guruh ma'lumotlari alohida
    for g_id, info in list(guruhlar.items())[:50]:
        # Bot hali guruhda borligini tekshiramiz
        try:
            chat = await bot.get_chat(int(g_id))
            guruh_ismi = chat.title or g_id
            # Bot memberni tekshiramiz
            bot_info = await bot.get_me()
            member = await bot.get_chat_member(int(g_id), bot_info.id)
            if member.status not in ("administrator", "creator", "member"):
                continue  # Bot guruhda yo'q - o'tkazib yuboramiz
        except:
            continue  # Guruhga kira olmasa - o'tkazib yuboramiz

        faol_guruhlar += 1

        # Guruh xatim soni
        g_xatim = sum(
            s.get("guruhlar", {}).get(g_id, {}).get("jami_xatim", 0)
            for s in stats_db.values()
        )

        # Kim qo'shgani
        qoshgan = users_db.get(info["qoshgan"], {}).get("ism", "Noma'lum")

        guruh_lines.append(
            f"🏠 <b>{guruh_ismi}</b>\n"
            f"   👥 A'zolar: {info['azolar']} kishi\n"
            f"   📖 Xatimlar: {g_xatim} ta\n"
            f"   ➕ Qo'shgan: {qoshgan}\n"
        )

    # Yakuniy xabarni yig'amiz
    lines = [
        "👑 <b>SUPER ADMIN PANEL</b>\n",
        f"👤 Jami foydalanuvchilar: <b>{jami_user}</b>",
        f"💬 Faol guruhlar: <b>{faol_guruhlar}</b>",
        f"📖 Jami xatimlar: <b>{jami_xatim}</b>\n",
        "─────────────────────",
        "📋 <b>Guruhlar ro'yxati:</b>\n",
    ] + guruh_lines

    await message.answer("\n".join(lines))


# ── /xabar ──
@dp.message(Command("xabar"))
async def cmd_broadcast(message: types.Message):
    if not message.from_user or message.from_user.id != SUPER_ADMIN_ID:
        return
    if not message.reply_to_message:
        return await message.answer("Xabar yuborish uchun biror xabarga reply qiling!")

    yuborildi = 0
    yuborilmadi = 0
    for uid_str in users_db:
        try:
            await bot.copy_message(
                chat_id=int(uid_str),
                from_chat_id=message.chat.id,
                message_id=message.reply_to_message.message_id
            )
            yuborildi += 1
        except:
            yuborilmadi += 1

    await message.answer(f"✅ Yuborildi: {yuborildi}\n❌ Yuborilmadi: {yuborilmadi}")


# ── Guruh a'zolarini saqlash (eng oxirida!) ──
@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def track_users(message: types.Message):
    if not message.from_user:
        return
    uid = str(message.from_user.id)
    uname = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    chat_id = str(message.chat.id)
    if uid not in users_db:
        users_db[uid] = {"ism": uname, "guruhlar": []}
    users_db[uid]["ism"] = uname
    if "guruhlar" not in users_db[uid]:
        users_db[uid]["guruhlar"] = []
    if chat_id not in users_db[uid]["guruhlar"]:
        users_db[uid]["guruhlar"].append(chat_id)
        save_json(USERS_FILE, users_db)


async def main():
    await bot.set_my_commands([
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="xatimyaratish", description="Yangi xatim yaratish"),
        BotCommand(command="statistika", description="Shaxsiy statistika"),
        BotCommand(command="tarix", description="Guruh xatim tarixi"),
        BotCommand(command="reyting", description="Eng faol qatnashchilar"),
    ])
    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
