import asyncio
import datetime
import logging
import time
from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import List

import aiohttp
import anyio
import pymorphy2
from async_timeout import timeout

import adapters
from adapters import SANITIZERS
from text_tools import split_by_words, calculate_jaundice_rate

TEST_ARTICLES = (
    "https://inosmi.ru/20220223/maslo-253083812.html",
    "https://inosmi.ru/20220221/pitanie-253119215.html",
    "https://inosmi.ru/20220223/chay-253152243.html",
    "https://inosmi.ru/20220222/pitanie-253134875.html",
    "https://inosmi.ru/20220222/sol-253124517.html",
    "http://inosmi.ru/economic/20190629/245384784.html"
)

analyzer = pymorphy2.MorphAnalyzer()
TIMEOUT = 3
logging.basicConfig(level=logging.INFO)


class ProcessingStatus(Enum):
    OK = 'OK'
    FETCH_ERROR = 'FETCH_ERROR'
    PARSING_ERROR = 'PARSING_ERROR'
    TIMEOUT = 'TIMEOUT'


@dataclass
class Result:
    status: ProcessingStatus
    article_url: str
    rate: float
    words_count: int

    def __str__(self):
        return (f"Статус: {self.status.value}\n"
                f"URL: {self.article_url}\n"
                f"Рейтинг: {self.rate}\n"
                f"Слов в статье: {self.words_count}")


async def fetch(session: aiohttp.ClientSession, url):
    async with timeout(TIMEOUT):
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()


@contextmanager
def log_execution_time():
    start_time = time.monotonic()
    try:
        yield
    finally:
        logging.info(f"Анализ закончен за {time.monotonic() - start_time:.2f} сек")


async def process_single_article(article_url, session, negative_words, result: List[Result]):
    sanitizer = SANITIZERS["inosmi_ru"]
    status = ProcessingStatus.OK
    rate = None
    words_count = None
    with log_execution_time():
        try:
            html = await fetch(session, article_url)
            article = sanitizer(html, True)
        except aiohttp.ClientError:
            status = ProcessingStatus.FETCH_ERROR
        except adapters.ArticleNotFound:
            status = ProcessingStatus.PARSING_ERROR
        except asyncio.TimeoutError:
            status = ProcessingStatus.TIMEOUT
        else:
            words = split_by_words(analyzer, article)
            rate = calculate_jaundice_rate(words, negative_words)
            words_count = len(words)
    result.append(Result(status, article_url, rate, words_count))


async def process_articles(article_urls) -> List[Result]:
    with open("charged_dict/negative_words.txt") as file:
        negative_words = split_by_words(analyzer, file.read())
    result: List[Result] = []
    async with aiohttp.ClientSession() as session:
        async with anyio.create_task_group() as tg:
            for article in article_urls:
                tg.start_soon(process_single_article, article, session, negative_words, result)
    return result


