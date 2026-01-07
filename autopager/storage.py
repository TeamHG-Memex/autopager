# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import io
import csv
import parsel

from autopager.htmlutils import get_xseq_yseq


DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
DEFAULT_LABEL_MAP = {
    'PREV': 'PREV',
    'NEXT': 'NEXT',
    'PAGE': 'PAGE',

    'FIRST': 'PAGE',
    'LAST': 'PAGE',
}


class Storage(object):

    def __init__(self, path=DEFAULT_DATA_PATH, label_map=DEFAULT_LABEL_MAP):
        self.path = path
        self.label_map = label_map

    def get_Xy(self, validate=True):
        X, y = [], []
        for row in self.iter_records():
            html = self._load_html(row)
            selectors = {key: row[key] for key in self.label_map.keys()}
            root = parsel.Selector(html)
            xseq, yseq = get_xseq_yseq(root, selectors, validate=validate)
            yseq = [self.label_map.get(_y, _y) for _y in yseq]
            X.append(xseq)
            y.append(yseq)
        return X, y

    def iter_records(self):
        info_path = os.path.join(self.path, 'data.csv')
        with io.open(info_path, encoding='utf8') as f:
            for row in csv.DictReader(f):
                if row['failed']:
                    continue
                yield row

    def _load_html(self, row):
        data_path = os.path.join(self.path, 'html')
        path = os.path.join(data_path, row['File Name'] + ".html")
        with io.open(path, encoding=row['Encoding']) as f:
            return f.read()
