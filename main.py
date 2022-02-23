import aiohttp
import asyncio
from adapters import SANITIZERS


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def main():
    sanitizer = SANITIZERS["inosmi_ru"]
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'https://inosmi.ru/20220221/pitanie-253119215.html')
        article = sanitizer(html)
        print(article)


if __name__ == '__main__':
    asyncio.run(main())
