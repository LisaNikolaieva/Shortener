import asyncio
from aiohttp import web
from db import setup_db
from bson import ObjectId
import re

async def shut_url_get(request):
    form_request = """
    <form action="/" method="POST">
  <div>
    <label for="user_url">Enter your URL</label>
    <input name="user_url" id="user_url" value="" />
  </div>

  <div>
    <button>Send URL</button>
  </div>
</form>
    """
    return web.Response(text=form_request, content_type='text/html')


async def shut_url_post(request):
    result = await request.text()
    user_url = result.replace('user_url=', '')
    user_url_list = user_url.split('://') #re.sub(r"https?://", '', user_url)
    db = request.app["db"]
    collection = db['shortener']
    url_record = await collection.insert_one({'user_url': user_url_list[1], 'prefix': user_url_list[0]})
    return web.Response(text=str(url_record.inserted_id))


async def handle(request):
    name_url = request.match_info.get('name')
    db = request.app["db"]
    collection = db['shortener']
    obj_url = await collection.find_one({"_id":  ObjectId(name_url)})
    prefix = obj_url.get('prefix', 'http')
    url = obj_url['user_url']
    return web.HTTPFound(prefix + '://' + url)


db = asyncio.run(setup_db())
app = web.Application()

app.add_routes([web.get('/', shut_url_get),
                web.get('/{name}', handle),
                web.post('/', shut_url_post)])
app["db"] = db

if __name__ == '__main__':
    web.run_app(app)
