# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re
from itertools import chain

import tldextract


def get_domain(url):
    """
    >>> get_domain('example.org')
    'example'
    >>> get_domain('foo.example.co.uk')
    'example'
    """
    return tldextract.extract(url).domain


tokenize = re.compile(r"(?u)\b\w+\b").findall
""" Tokenize text """


_replace_white_spaces = re.compile(r"\s\s+").sub
_replace_newlines = re.compile(r'[\n\r]').sub
def normalize_whitespaces(text):
    """ Replace newlines and whitespaces with a single white space """
    text = _replace_newlines(" ", text)
    return _replace_white_spaces(" ", text)


def ngrams(seq, min_n, max_n):
    """
    Generate min_n to max_n n-grams of elements from a given sequence.
    """
    text_len = len(seq)
    for n in range(min_n, min(max_n + 1, text_len + 1)):
        for i in range(text_len - n + 1):
            yield seq[i: i + n]


def normalize(text):
    """ Default text normalization function """
    return normalize_whitespaces(text.lower())


def ngrams_stripped(text, min_n, max_n):
    for txt in ngrams(text, min_n, max_n):
        stripped = txt.strip()
        if stripped:
            yield stripped


def ngrams_wb(text, min_n, max_n, include_tokens=True):
    """
    Generate character ngrams; they don't span across whitespaces.
    If ``include_tokens`` is True, tokens themselves are included
    if their lenght is less than ``min_n``.

    >>> list(ngrams_wb("I am hungry", 3, 4))
    ['hun', 'ung', 'ngr', 'gry', 'hung', 'ungr', 'ngry', 'I', 'am']
    >>> list(ngrams_wb("I am hungry", 3, 4, include_tokens=False))
    ['hun', 'ung', 'ngr', 'gry', 'hung', 'ungr', 'ngry']
    """
    tokens = text.split()
    for t in tokens:
        for ngram in ngrams_stripped(t, min_n, max_n):
            yield ngram
    if include_tokens:
        for t in tokens:
            if len(t) < min_n:
                yield t


def replace_digits(text, repl='X'):
    """
    >>> replace_digits("hello, 123!")
    'hello, XXX!'
    """
    return re.sub('\d', repl, text)

