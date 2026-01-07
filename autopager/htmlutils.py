# -*- coding: utf-8 -*-
from __future__ import absolute_import  
import parsel
from autopager.utils import normalize_whitespaces


def get_links_loose(sel):
    """
    Return ``<a>`` elements for a selector.

    If selection is inside <a> element, this parent <a> element is returned.
    If selection is <a> element, it is returned.
    If selection has <a> children, they are returned.
    """
    return parsel.SelectorList(_get_links(sel))


def _get_links(sel):
    for el in sel:
        links_parent = el.xpath('ancestor::a')
        if links_parent:
            for link in links_parent:
                yield link
        else:
            for link in el.css('a'):
                yield link


def get_links(sel):
    return sel.xpath(".//a[@href]")


def get_xseq_yseq(root, selectors, validate=True):
    """
    Extract links from selector ``root`` and assign each link a class label
    if it matches one of the ``selectors`` or "O" if it matches none of them.
    Only ``<a>`` elements with ``href`` attributes are returned.

    ``selectors`` is a ``{label: selector}`` dict.

    When ``validate`` is True this function checks that each selector
    returns non-empty result, and that results don't overlap; in case of
    errors it prints error messages.
    """
    xseq = get_links(root)
    links_extracted = xseq.extract()
    classes = ["O"] * len(xseq)

    for label, selector in selectors.items():
        if not selector:
            continue
        sel_links = set(get_links_loose(root.css(selector)).extract())
        if validate and not sel_links:
            print("error: links not found", label, selector)
        matched_links = set()
        for idx, link in enumerate(links_extracted):
            if link in sel_links:
                if validate and classes[idx] != 'O':
                    print("warning: link is classified in more than 1 classes",
                          link, label)
                matched_links.add(link)
                classes[idx] = label
        if validate and matched_links != sel_links:
            print("Not all links are matched", sel_links - matched_links)

    return xseq, classes


def get_link_text(link):
    """
    Return text of <a> element: either its string contents or the 'alt'
    of <img> tags inside.
    """
    txt = ' '.join(link.xpath('string()').extract())
    if not txt:
        txt = ' '.join(link.xpath('.//img/@alt').extract())
    return txt


def get_link_href(a):
    return a.xpath('@href').extract_first()


def get_text_around_selector_list(sel_list, max_length=150):
    """
    Return a list of (before, after) tuples with text for each element
    in ``sel_list`` parsel.SelectorList. Max text length can be set via
    ``max_length`` argument.
    """
    if not sel_list:
        return []
    doc_root = list(get_selector_root(sel_list[0]).iterancestors())[-1]
    elems = [get_selector_root(sel) for sel in sel_list]
    before, after = get_text_around_elems(doc_root, elems)
    return [(before[el][-max_length:], after[el][:max_length]) for el in elems]


def get_selector_root(sel):
    """ Return lxml Element for a Selector """
    if not hasattr(sel, 'root'):
        # scrapy.Selector, scrapy < 1.1
        return sel._root
    # parsel.Selector or scrapy.Selector, scrapy >= 1.1
    return sel.root


# XXX: this function is copied from formasaurus.
# Time to create an utility library?
def get_text_around_elems(tree, elems):
    """
    Return (before, after) tuple with {elem: text} dicts containing
    text before a specified lxml DOM Element and after it.
    """
    if not elems:
        return {}, {}
    buf = []
    before = {elem: '' for elem in elems}
    after = {elem: '' for elem in elems}

    def flush_buf():
        res = '  '.join([
            normalize_whitespaces(b.strip())
            for b in buf
            if b and b.strip()
        ])
        buf[:] = []
        return res

    def visit(elem):
        if elem in before:
            before[elem] = flush_buf()
            buf.append(elem.tail)
            return
        buf.append(elem.text)
        for child in elem:
            visit(child)
        buf.append(elem.tail)

    visit(tree)

    for prev, next in zip(elems[:-1], elems[1:]):
        after[prev] = before[next]

    after[elems[-1]] = flush_buf()
    return before, after
