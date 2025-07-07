import os
import json
import asyncio
import requests
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.payments import GetStarGiftsRequest

# ⬇️ .env fayldan o‘qish
load_dotenv()

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
chat_id = int(os.getenv('CHAT_ID'))
check_interval = int(os.getenv('CHECK_INTERVAL', 15))

client = TelegramClient('giftbot-session', api_id, api_hash)
sent_gift_ids = set()

# 📅 Sana formatlash
def format_date(dt):
    return dt.strftime('%Y-%m-%d %H:%M') if dt else "Noma’lum"

# 💬 Matnli xabar yuborish
async def send_telegram_message(text, reply_markup=None):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print('✅ Matn yuborildi!')
        else:
            print(f"⚠️ Matn xatolik: {response.text}")
    except Exception as e:
        print(f"⚠️ Matn yuborishda xato: {e}")

# 🖼 Rasmli xabar yuborish
async def send_telegram_photo(text, photo_bytes):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    payload = {
        'chat_id': chat_id,
        'caption': text,
        'parse_mode': 'HTML'
    }
    files = {'photo': ('gift.jpg', photo_bytes)}
    try:
        response = requests.post(url, data=payload, files=files)
        if response.status_code == 200:
            print('✅ Rasm yuborildi!')
        else:
            print(f"⚠️ Rasm xatolik: {response.text}")
    except Exception as e:
        print(f"⚠️ Rasm yuborishda xato: {e}")

# 🧷 Sotib olish tugmasi
def get_buy_button(gift_id):
    return {
        "inline_keyboard": [[
            {
                "text": "💳 Sotib olish",
                "url": f"https://t.me/stars?start={gift_id}"
            }
        ]]
    }

# 🎁 Giftlarni tekshirish
async def check_gifts():
    global sent_gift_ids

    if not client.is_connected():
        print("🔌 Telegramga ulanmoqda...")
        await client.connect()

    print('🎁 Giftlarni tekshiryapmiz...')
    result = await client(GetStarGiftsRequest(hash=0))
    gifts = [gift for gift in result.gifts if not gift.sold_out]

    if not gifts:
        print('❌ Gift topilmadi.')
        return

    for gift in gifts:
        if gift.id in sent_gift_ids:
            continue

        sent_gift_ids.add(gift.id)

        msg = (
            f"🎁 <b>Yangi Gift!</b>\n"
            f"🆔 ID: <code>{gift.id}</code>\n"
            f"💲 Narxi: <b>{gift.stars} stars</b>\n"
            f"📦 Qolgan: <b>{gift.availability_remains}/{gift.availability_total}</b>\n"
            f"📅 Boshlanishi: <b>{format_date(gift.first_sale_date)}</b>\n"
            f"📅 Tugashi: <b>{format_date(gift.last_sale_date)}</b>\n"
            f"🔒 Cheklangan: {'✅' if gift.limited else '❌'}"
        )

        reply_markup = get_buy_button(gift.id)

        # 🖼 Thumbnail yuklash
        photo_bytes = None
        if gift.sticker and gift.sticker.thumbs:
            try:
                thumb = gift.sticker.thumbs[0]
                byte_stream = BytesIO()
                await client.download_media(thumb, file=byte_stream)
                byte_stream.seek(0)
                photo_bytes = byte_stream.read()
                print("🖼 Thumbnail yuklandi.")
            except Exception as e:
                print(f"⚠️ Thumbnail xato: {e}")

        if photo_bytes:
            await send_telegram_photo(msg, photo_bytes)
        else:
            await send_telegram_message(msg, reply_markup=reply_markup)

# 🔁 Asosiy ish jarayoni
async def main():
    print('🔑 Telegramga ulanmoqda...')
    await client.start()
    me = await client.get_me()
    print(f'✅ Kirildi: @{me.username or me.first_name}')

    while True:
        try:
            await check_gifts()
        except Exception as e:
            print(f"⚠️ Xatolik: {e}")
        await asyncio.sleep(check_interval)

# ▶️ Ishga tushirish
if __name__ == "__main__":
    asyncio.run(main())
