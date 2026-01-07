# -*- coding: utf-8 -*-
from __future__ import absolute_import  
import pytest

from autopager.utils import normalize_whitespaces, ngrams, normalize


@pytest.mark.parametrize(["text", "result"], [
    ["Hello    \tworld!", "Hello world!"],
    ["\nI\nam\n\r  hungry  ", " I am hungry "],
])
def test_normalize_whitespaces(text, result):
    assert normalize_whitespaces(text) == result


@pytest.mark.parametrize(["seq", "min_n", "max_n", "result"], [
    ["Hello", 2, 3, ["He", "el", "ll", "lo", "Hel", "ell", "llo"]],
    [["I", "am", "hungry"], 1, 2, [["I"], ["am"], ["hungry"], ["I", "am"], ["am", "hungry"]]],
])
def test_ngrams(seq, min_n, max_n, result):
    assert list(ngrams(seq, min_n, max_n)) == result


def test_normalize():
    assert normalize("Hello,\n  world!") == "hello, world!"
