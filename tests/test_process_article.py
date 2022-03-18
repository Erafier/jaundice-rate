import asyncio
import pytest
from main import process_articles, Result, ProcessingStatus

PATH_TO_WORDS = "../charged_dict/negative_words.txt"


@pytest.fixture
def correct_article():
    return "https://inosmi.ru/20220223/maslo-253083812.html",


TEST_ARTICLES = (
    "https://inosmi.ru/20220223/maslo-253083812.html",
    "https://inosmi.ru/20220221/pitanie-253119215.html",
    "https://inosmi.ru/20220223/chay-253152243.html",
    "https://inosmi.ru/20220222/pitanie-253134875.html",
    "https://inosmi.ru/20220222/sol-253124517.html",
    "https://inosmi.ru/economic/20190629/245384784.html"
)


@pytest.mark.asyncio
@pytest.mark.parametrize("article, expected", [(
    ["https://inosmi.ru/20220223/maslo-253083812.html"], [Result(
        ProcessingStatus.OK,
        "https://inosmi.ru/20220223/maslo-253083812.html",
        1.81,
        719
    )]
),
    (
        ["https://wrong.url"], [Result(
            ProcessingStatus.FETCH_ERROR,
            "https://wrong.url",
            None,
            None
        )]
    ),
    (
        ["https://e1.ru/"], [Result(
            ProcessingStatus.PARSING_ERROR,
            "https://e1.ru/",
            None,
            None
        )]
    )
])
async def test_process(article, expected):
    result = await process_articles(article, PATH_TO_WORDS)
    assert result == expected
