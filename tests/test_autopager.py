# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

import autopager
from autopager.autopager import train_crf


DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'autopager', 'data')

PAGE = u"""
<html>
    <body>
        Pages:
        <div class="paginator">
            <a href="/blog/?page=1" class="prev">&lt;</a>
            <a href="/blog/?page=1">1</a>
            <span class="active">2</a>
            <a href="/blog/?page=3">3</a>
            <a href="/blog/?page=4" class="last">4</a>
            <a href="/blog/?page=3" class="next">&gt;</a>
        </div>
    </body>
</html>
"""


def test_training_and_extraction(tmpdir):
    model_path = str(tmpdir.join('model.crf'))
    train_crf(DATA_PATH, model_path)

    pager = autopager.AutoPager(path=model_path)

    assert pager.urls(PAGE) == [
        "/blog/?page=1",
        "/blog/?page=1",
        "/blog/?page=3",
        "/blog/?page=4",
        "/blog/?page=3",
    ]

    assert pager.urls(PAGE, "http://example.com") == [
        "http://example.com/blog/?page=1",
        "http://example.com/blog/?page=1",
        "http://example.com/blog/?page=3",
        "http://example.com/blog/?page=4",
        "http://example.com/blog/?page=3",
    ]

    types = [tp for (tp, link) in pager.extract(PAGE)]
    assert types == ['PREV', 'PAGE', 'PAGE', 'PAGE', 'NEXT']

    assert pager.urls(PAGE, direct=False) == [
        "/blog/?page=1",
        "/blog/?page=3",
    ]

    last_page = pager.select(PAGE).css(".last")
    assert last_page.xpath("@href").extract_first() == "/blog/?page=4"
