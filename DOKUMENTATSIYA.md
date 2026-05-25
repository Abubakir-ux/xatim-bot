Xatim.uz Bot — Texnik Dokumentatsiya

Loyiha haqida

Telegram bot — guruhda Qur'on xatimini tashkil qilish uchun. Python + aiogram 3.x.

Fayl tuzilmasi

Xatim.uz/

├── main.py          # Asosiy bot kodi

├── database.py      # SQLite baza (yangi, hali to'liq integratsiya qilinmagan)

├── requirements.txt # aiogram==3.7.0

├── xatim.db         # SQLite fayl (database.py dan)

├── users.json       # Foydalanuvchilar (hozirgi baza)

├── stats.json       # Statistika (hozirgi baza)

└── tarix.json       # Xatim tarixi (hozirgi baza)

Hozirgi holat

Baza: JSON fayllar (users.json, stats.json, tarix.json)

SQLite (database.py) yozildi lekin main.py ga hali ulanmagan — keyingi ish shu.

main.py — Asosiy o'zgaruvchilar

pythonAPI_TOKEN = '...'

SUPER_ADMIN_ID = 7480459140

xatm_db = {}        # Aktiv xatimlar (xotirada)

tarix_db = {}       # JSON dan yuklangan

stats_db = {}       # JSON dan yuklangan

users_db = {}       # JSON dan yuklangan

broadcast_mode = set()  # /xabar uchun

Commandalar

CommandKimQayerda/startHammaLichka/xatimyaratishHammaGuruh/statistikaHammaGuruh/tarixHammaGuruh/reytingHammaGuruh/adminGuruh admin + Super adminGuruh + Lichka/xabarSuper adminLichka/myidHammaВезде

Callbacks

CallbackVazifajoin_Xatimga qo'shilishleave_Xatimdan chiqishboshlash_Xatimni boshlash (admin)tayyor_Juzni o'qib bo'ldim (guruhda)pm_tayyor_Juzni o'qib bo'ldim (lichkada)pm_keyin_3 soatdan keyin eslatmanoop_Hech narsa (O'qiganlar tugmasi)

Xatim jarayoni

/xatimyaratish

    ↓

Xabar yaratiladi → xatm_db ga saqlanadi

    ↓

Guruh a'zolariga lichkaga bildirishnoma → "Guruhga o'tish" tugmasi

    ↓

Odamlar ➕ Qo'shilish bosadi

    ↓

Admin 📖 Boshlash bosadi

    ↓

30 juz taqsimlanadi (tasodifiy)

Her bir qatnashchiga lichkaga eslatma yuboriladi

    ↓

Har kim ✅ O'qidim bosadi

    ↓

Hammasi o'qiganda 🎉 Xatim yakunlandi!

taqsimla() funksiyasi

30 juzni qatnashuvchilar soniga bo'ladi

Har biri kamida 1 juz

Tasodifiy taqsimlash

30 dan ko'p odam bo'lsa — har biriga 1 tadan (faqat 30 ta oladi) ⚠️ Bu muammo — keyingi ish

JUZ_INFO

30 ta juz, har biri qaysi suradan boshlanib tugashini ko'rsatadi.

pythonJUZ_INFO = {1: "Al-Fotiha 1 - Al-Baqara 141", ... 30: "An-Naba 1 - An-Nos 6"}

Keyingi ishlar (prioritet bo'yicha)

database.py ni main.py ga ulash — JSON o'rniga SQLite ishlatish

30 dan ko'p odam muammosi — 2x, 3x xatim tanlash

PDF/rasm natija — xatim yakunida chiroyli karta

Server

Railway.app da deploy qilingan

GitHub repo: Abubakir-ux/xatim-bot

Auto-deploy: har git push da yangilanadi

Muhim eslatmalar

track_users handler eng oxirida turishi shart

broadcast_mode — set(), /xabar bosganida user ID qo'shiladi

Eslatma: asyncio.create_task(qayta_eslatma(...)) — 3 soat kutadi

Bot guruhda admin bo'lishi kerak
