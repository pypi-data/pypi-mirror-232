import pytest  # noqa: F401

import karentify


def test_karentify():
    karentify.tiktok = None
    assert karentify.karentify('I want to buy a damburger') == 'I WaNt tO BuY A DaMbUrGeR!!!'
    karentify.tiktok = None
    assert karentify.karentify('i want to buy a damburger') == 'i wAnT To bUy a dAmBuRgEr!!!'
