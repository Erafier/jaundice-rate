from bs4 import BeautifulSoup

from .exceptions import ArticleNotFound


def sanitize(html, plaintext=False):
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.select("div.article__text")

    if len(paragraphs) <= 1:
        raise ArticleNotFound()

    text = ""

    for paragraph in paragraphs:
        paragraph = paragraph.get_text() if plaintext else str(paragraph)
        text += " " + paragraph

    return text.strip()
