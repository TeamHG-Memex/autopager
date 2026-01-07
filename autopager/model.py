# -*- coding: utf-8 -*-
"""

XXX: also tried, but not present in the final model:

* a feature which is 1 if the current link text is a number ``i`` and
  previous link text is ``i-1``;
* extracting number patterns from link text: replacing digits with X and
  characters with C (currently only numbers are replaced);
* replacing numbers with X, not just individual digits;
* character ngrams from raw link href (currently path and query are processed
  separately);
* using query parameter values, not only query parameter names;
* using element id and title attributes;
* all character ngrams or tokens from URL path (currently only a few hardcoded
  features based on path are used);
* string distance between link URL and page URL (Jaro-Winkler on absolute URLs
  was tried; for good results more URL preprocessing is needed);
* distance between URL components (a customized Jaccard distance)


"""
from __future__ import absolute_import

import re
from itertools import islice

import sklearn_crfsuite
from six.moves.urllib.parse import urlsplit, parse_qsl

from autopager.htmlutils import (
    get_link_text,
    get_link_href,
    get_text_around_selector_list,
    get_selector_root,
)
from autopager.limits import Limits
from autopager.utils import normalize, tokenize, ngrams_wb, replace_digits


AUTOPAGER_LIMITS = Limits()


def _elem_attr(elem, attr):
    return normalize(elem.get(attr, ''))


def _num_tokens_feature(text):
    num_tokens = len(tokenize(text))
    if num_tokens > 2:
        num_tokens = '>2'
    else:
        num_tokens = "=%s" % num_tokens
    return num_tokens


def _as_list(generator, limit=None):
    """
    >>> _as_list(ngrams_wb("text", 2, 2), 0)
    []
    >>> _as_list(ngrams_wb("text", 2, 2), 2)
    ['te', 'ex']
    >>> _as_list(ngrams_wb("text", 2, 2))
    ['te', 'ex', 'xt']
    """
    return list(generator if limit is None else islice(generator, 0, limit))


def link_to_features(link):
    text = normalize(get_link_text(link))

    href = get_link_href(link)
    p = urlsplit(href)

    query_parsed = parse_qsl(p.query)
    query_param_names = [k.lower() for k, v in query_parsed]
    query_param_names_ngrams = _as_list(ngrams_wb(
        " ".join([normalize(name) for name in query_param_names]), 3, 5, True
    ))

    elem = get_selector_root(link)
    elem_target = _elem_attr(elem, 'target')
    elem_rel = _elem_attr(elem, 'rel')

    # Classes of link itself and all its children.
    # It is common to have e.g. span elements with fontawesome
    # arrow icon classes inside <a> links.
    self_and_children_classes = ' '.join(link.xpath(".//@class").extract())
    parent_classes = ' '.join(link.xpath('../@class').extract())
    css_classes = normalize(parent_classes + ' ' + self_and_children_classes)

    return {
        'bias': 3.0,
        'isdigit': text.isdigit(),
        'isalpha': text.isalpha(),
        'elem-target': elem_target,
        'elem-rel': elem_rel,
        'num-tokens%s' % _num_tokens_feature(text): 1.0,

        'text': _as_list(ngrams_wb(replace_digits(text), 2, 5),
                         AUTOPAGER_LIMITS.max_text_features),
        'text-exact': replace_digits(text.strip()[:20].strip()),
        'class': _as_list(ngrams_wb(css_classes, 4, 5),
                          AUTOPAGER_LIMITS.max_css_features),
        'query': query_param_names_ngrams,

        'path-has-page': 'page' in p.path.lower(),
        'path-has-pageXX': re.search(r'[/-](?:p|page\w?)/?\d+', p.path.lower()) is not None,
        'path-has-number': any(part.isdigit() for part in p.path.split('/')),

        'href-has-year': re.search('20\d\d', href) is not None,
    }

    # Unused features
    # ===============
    #
    # href_ngrams = ngrams_striped(p.path + '?' + p.query, 5, 5)
    # query_param_patterns = [
    #     "%s=%s" % (k.lower(), number_pattern(v, ratio=0.0).strip())
    #     for k, v in query_parsed
    # ]
    # path_tokens = tokenize(number_pattern(p.path.lower(), 0.1))
    # path_ngrams = ngrams_striped(p.path, 4, 4)
    # query_ngrams = ngrams_striped(p.query, 4, 4)
    #
    # path_tokens = ngrams_wb(replace_digits(p.path.lower().replace('/', ' ')), 3, 5)
    # elem_css_class = _elem_attr(elem, 'class')
    # elem_id = _elem_attr(elem, 'id')
    # elem_title = _elem_attr(elem, 'title')
    #
    # path = path_tokens
    # bad_href = "javascript://" in _href or p.fragment and (not p.query or p.path)
    # title = ngrams_wb(replace_digits(normalize(elem_title)), 4, 5)
    #
    # 'css-class-ngrams': ngrams_striped(link_classes, 4, 5),
    # 'css-parent-class-ngrams': ngrams_striped(parent_classes, 4, 5),
    # 'query_param_name': query_param_names,
    # 'query_param_pattern': query_param_patterns,
    # 'path_tokens': path_tokens,
    # 'text_pattern': normalize(text_pattern),
    # 'text_ngrams': text_ngrams,
    #
    # 'id': ngrams_wb(elem_id, 4, 4),
    # 'id-class-ngrams': ngrams_striped(elem_css_class + ' ' + elem_id, 5, 5),
    # 'id': tokenize(elem_id),


def page_to_features(xseq):
    features = [link_to_features(a) for a in xseq]
    around = get_text_around_selector_list(xseq, max_length=15)

    # weight is less than 1 because there is a lot of duplicate information
    # in these ngrams and so we want to regularize them stronger
    # (as if they are a single feature, not many features)
    k = 0.2
    for feat, (before, after) in zip(features, around):
        feat['text-before'] = {n: k for n in _as_list(ngrams_wb(normalize(before), 5, 5))}
        feat['text-after'] = {n: k for n in _as_list(ngrams_wb(normalize(after), 5, 5))}
    return features


def get_crf(**kwargs):
    params = dict(
        algorithm='lbfgs',
        c1=0.001,
        c2=0.05,
        max_iterations=100,
        all_possible_transitions=True,
        verbose=False,
    )
    params.update(kwargs)
    return sklearn_crfsuite.CRF(**params)
