import pytest
import requests

from adapters import ArticleNotFound
from adapters.inosmi_ru import sanitize


def test_sanitize():
    resp = requests.get('https://inosmi.ru/economic/20190629/245384784.html')
    resp.raise_for_status()
    clean_text = sanitize(resp.text)

    assert clean_text.startswith('<div class="article__text">')
    assert clean_text.endswith('</div>')
    assert 'В субботу, 29 июня, президент США Дональд Трамп' in clean_text
    assert 'За несколько часов до встречи с Си' in clean_text

    assert '<p dir="ltr">' in clean_text
    assert '</p>' in clean_text

    clean_plaintext = sanitize(resp.text, plaintext=True)

    assert 'В субботу, 29 июня, президент США Дональд Трамп' in clean_plaintext
    assert 'За несколько часов до встречи с Си' in clean_plaintext

    assert '<p dir="ltr">' not in clean_plaintext
    assert '</p>' not in clean_plaintext
    assert '<div>' not in clean_plaintext
    assert '</div>' not in clean_plaintext


def test_sanitize_wrong_url():
    resp = requests.get('http://example.com')
    resp.raise_for_status()
    with pytest.raises(ArticleNotFound):
        sanitize(resp.text)
