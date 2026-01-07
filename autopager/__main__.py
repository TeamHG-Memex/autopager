#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AutoPager command-line utility.

Usage:
    autopager train <data-path> <modelfile>
    autopager -h | --help
    autopager --version

To train the autopager use "train" command.
"""
from __future__ import absolute_import, print_function
import docopt
import autopager
from autopager.autopager import train_crf


def main():
    args = docopt.docopt(__doc__, version=autopager.__version__)
    if args['train']:
        train_crf(args['<data-path>'], args['<modelfile>'])


if __name__ == '__main__':
    main()
