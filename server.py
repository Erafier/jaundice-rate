import dataclasses

import aiohttp.web
from aiohttp import web
from main import process_articles


async def handle(request: aiohttp.web.Request):
    urls = request.query.get("urls")
    if urls:
        urls = urls.strip().split(",")
    if not urls:
        raise web.HTTPBadRequest(text="Empty urls")
    elif len(urls) > 10:
        raise web.HTTPBadRequest(text="Too many urls in request, should be 10 or less")
    result = await process_articles(urls)
    return web.json_response([{
        "status": article.status.value,
        "url": article.article_url,
        "score": article.rate,
        "words_count": article.words_count
    } for article in result])


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    web.run_app(app)
