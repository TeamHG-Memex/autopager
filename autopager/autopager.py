# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import six
from six.moves.urllib.parse import urljoin
import six.moves.cPickle as pickle

import parsel
from autopager.htmlutils import get_links
from autopager.model import page_to_features, get_crf, AUTOPAGER_LIMITS
from autopager.storage import Storage


auto = object()


def urls(page, baseurl=auto, direct=True, prev=True, next=True):
    """
    Return a list of pagination URLs extracted form the page.
    When baseurl is None relative URLs are returned; pass baseurl
    to get absolute URLs.

    ``prev``, ``next`` and ``direct`` arguments control whether to return
    'next page', 'previous page' links and links to specific pages.
    By default, all link types are returned.
    """
    return get_shared_autopager().urls(page, baseurl, direct, prev, next)


def select(page, direct=True, prev=True, next=True):
    """
    Return parsel.SelectorList with pagination <a> elements.

    ``prev``, ``next`` and ``direct`` arguments control whether to return
    'next page', 'previous page' links and links to specific pages.
    By default, all link types are returned.
    """
    return get_shared_autopager().select(page, direct, prev, next)


def extract(page, direct=True, prev=True, next=True):
    """
    Return an iterator of (link_type, link) tuples with pagination links.
    link_type is one of "PAGE", "PREV" and "NEXT" constants;
    link is a parsel.Selector instance with pagination <a> element.

    ``prev``, ``next`` and ``direct`` arguments control whether to return
    'next page', 'previous page' links and links to specific pages.
    By default, all link types are returned.
    """
    return list(get_shared_autopager().extract(page, direct, prev, next))


class AutoPager(object):
    DEFAULT_CRF_PATH = os.path.join(os.path.dirname(__file__), 'autopager.crf')

    def __init__(self, path=None, crf=None):
        if crf is not None and path is not None:
            raise ValueError("Pass either path or a CRF instance")
        if crf is None and path is None:
            if not os.path.exists(self.DEFAULT_CRF_PATH):
                raise ValueError("CRF is not trained. If you've installed "
                                 "autopager from source repository you need"
                                 "to create the model yourselves from CLI "
                                 "using ``autopager train`` command.")
            path = self.DEFAULT_CRF_PATH
        if path is not None:
            with open(path, 'rb') as f:
                crf = pickle.load(f)
        self.crf = crf

    def urls(self, page, baseurl=auto, direct=True, prev=True, next=True):
        """
        Return a list of pagination URLs extracted form the page.
        When baseurl is None relative URLs are returned; pass baseurl
        to get absolute URLs.

        ``prev``, ``next`` and ``direct`` arguments control whether to return
        'next page', 'previous page' links and links to specific pages.
        By default, all link types are returned.
        """
        urls = self.select(page, direct, prev, next).xpath("@href").extract()
        if baseurl is auto:
            baseurl = _any2url(page)
        if baseurl is not None:
            urls = [urljoin(baseurl, url) for url in urls]
        return urls

    def select(self, page, direct=True, prev=True, next=True):
        """
        Return parsel.SelectorList with pagination <a> elements.

        ``prev``, ``next`` and ``direct`` arguments control whether to return
        'next page', 'previous page' links and links to specific pages.
        By default, all link types are returned.
        """
        links = self.extract(page, prev=prev, next=next, direct=direct)
        return parsel.SelectorList([x for y, x in links])

    def extract(self, page, direct=True, prev=True, next=True):
        """
        Return an iterator of (link_type, link) tuples with pagination links.
        link_type is one of "PAGE", "PREV" and "NEXT" constants;
        link is a parsel.Selector instance with pagination <a> element.

        ``prev``, ``next`` and ``direct`` arguments control whether to return
        'next page', 'previous page' links and links to specific pages.
        By default, all link types are returned.
        """
        sel = _any2selector(page)
        links = get_links(sel)
        links = links[:AUTOPAGER_LIMITS.max_links]
        xseq = page_to_features(links)
        yseq = self.crf.predict_single(xseq)
        for x, y in zip(links, yseq):
            if direct and y == 'PAGE':
                yield y, x
            if prev and y == 'PREV':
                yield y, x
            if next and y == 'NEXT':
                yield y, x


def _any2selector(data):
    if isinstance(data, parsel.Selector):
        return data

    if isinstance(data, bytes):
        raise ValueError("binary data is not supported")

    if isinstance(data, six.text_type):
        return parsel.Selector(text=data)

    # scrapy.Response support
    try:
        from scrapy.http import TextResponse
    except ImportError:
        pass
    else:
        if isinstance(data, TextResponse):
            return data.selector

    # requests.Response support
    return parsel.Selector(text=data.text)


def _any2url(data):
    return getattr(data, 'url', None)


def train_crf(data_path, out_path):
    """ Train CRF model using default parameters and save it to a file """
    storage = Storage(data_path)
    X_raw, y = storage.get_Xy(validate=False)
    X = [page_to_features(xseq) for xseq in X_raw]
    crf = get_crf()
    crf.fit(X, y)
    with open(out_path, 'wb') as f:
        pickle.dump(crf, f, protocol=2)


_instance = None

def get_shared_autopager():
    """ Return a shared AutoPager instance """
    global _instance
    if _instance is None:
        _instance = AutoPager()
    return _instance
