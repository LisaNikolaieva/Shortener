import asyncio
import os
import re
from aiogram import Bot, Dispatcher, types
from bson import ObjectId

from db import setup_db

BOT_TOKEN = os.environ.get('BOT_TOKEN') #"5743072896:AAHVL6xc2HierA5sBAV8YyAh_xl0hIKr2CQ"


async def start_handler(event: types.Message):
    await event.answer(
        f"Hello, {event.from_user.get_mention(as_html=True)} 👋!",
        parse_mode=types.ParseMode.HTML,
    )


async def url_handler(event: types.Message):
    db = await setup_db()
    collection = db['shortener']
    user_url = event.text
    user_url_list = user_url.split('://')  #re.sub(r"https?://", '', user_url)
    user_url_id = await collection.insert_one({'user_url': user_url_list[1], 'prefix': user_url_list[0]})
    url_id = user_url_id.inserted_id
    await event.answer(str(url_id))


async def send_url(event: types.Message):
    url_id = event.text
    db = await setup_db()
    collection = db['shortener']
    obj_url = await collection.find_one({"_id":  ObjectId(url_id)})
    prefix = str(obj_url.get('prefix', 'http'))
    url = str(obj_url.get('user_url'))
    await event.answer(prefix + "://" + url)

async def main():
    bot = Bot(token=BOT_TOKEN)
    try:
        disp = Dispatcher(bot=bot)
        disp.register_message_handler(start_handler, commands={"start", "restart"})
        disp.register_message_handler(url_handler, regexp='http.+')
        disp.register_message_handler(send_url, regexp='[a-z0-9]+')
        await disp.start_polling()
    finally:
        await bot.close()


asyncio.run(main())
