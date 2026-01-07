=========
Autopager
=========

.. image:: https://img.shields.io/pypi/v/autopager.svg
   :target: https://pypi.python.org/pypi/autopager
   :alt: PyPI Version

.. image:: https://img.shields.io/travis/TeamHG-Memex/autopager/master.svg
   :target: http://travis-ci.org/TeamHG-Memex/autopager
   :alt: Build Status

.. image:: http://codecov.io/github/TeamHG-Memex/autopager/coverage.svg?branch=master
   :target: http://codecov.io/github/TeamHG-Memex/autopager?branch=master
   :alt: Code Coverage


Autopager is a Python package which detects and classifies pagination links.

License is MIT.

Installation
============

Install autopager with pip::

   pip install autopager

Autopager depends on a few other packages like lxml_ and python-crfsuite_;
it will try install them automatically, but you may need to consult
with installation docs for these packages if installation fails.

.. _lxml: http://lxml.de/
.. _python-crfsuite: http://python-crfsuite.readthedocs.org/en/latest/

Autopager works in Python 3.6+.

Usage
=====

``autopager.urls`` function returns a list of pagination URLs::

   >>> import autopager
   >>> import requests
   >>> autopager.urls(requests.get('http://my-url.org'))
   ['http://my-url.org/page/1', 'http://my-url.org/page/3', 'http://my-url.org/page/4']

``autopager.select`` function returns all pagination ``<a>`` elements
as ``parsel.SelectorList`` (the same object as scrapy
response.css / response.xpath methods return).

``autopager.extract`` function returns a list of (link_type, link) tuples
where link_type is one of "PAGE", "PREV", "NEXT" and link
is a ``parsel.Selector`` instance.

These functions accept HTML page contents (as an unicode string),
requests Response or scrapy Response as a first argument.

By default, a prebuilt extraction model is used. If you want to use
your own model use ``autopager.AutoPager`` class; it has the same
methods but allows to provide model path or model itself::

   >>> import autopager
   >>> pager = autopager.AutoPager('my_model.crf')
   >>> pager.urls(html)

You also have to use AutoPager class if you've cloned repository from git;
prebuilt model is only available in pypi releases.

Detection Quality
=================

Web pages can be very different; autopager tries to work for all websites,
but some errors are inevitable. As a very rough estimate, expect it to work
properly for **9/10** paginators on websites sampled from 1M international
most popular websites (according to `Alexa Top`_).

.. _Alexa Top: https://support.alexa.com/hc/en-us/articles/200449834-Does-Alexa-have-a-list-of-its-top-ranked-websites-

Contributing
============

* Source code: https://github.com/TeamHG-Memex/autopager
* Issue tracker: https://github.com/TeamHG-Memex/autopager/issues

How It Works
============

Autopager uses machine learning to detect paginators. It classifies
``<a>`` HTML elements into 4 classes:

* PREV - previous page link
* PAGE - a link to a specific page
* NEXT - next page link
* OTHER - not a pagination link

To do that it uses features like link text, css class names,
URL parts and right/left contexts. CRF_ model is used for learning.

Web page is represented as a sequence of ``<a>`` elements. Only ``<a>``
elements with non-empty href attributes are in this sequence.

See also: https://github.com/TeamHG-Memex/autopager/blob/master/notebooks/Training.ipynb

.. _CRF: https://en.wikipedia.org/wiki/Conditional_random_field

Training Data
=============

Data is stored at autopager/data. Raw HTML source code
is in autopager/data/html folder. Annotations are in autopager/data/data.csv
file; elements are stored as CSS selectors.

Training data is annotated with 5 non-empty classes:

* PREV - previous page link
* PAGE - a link to a specific page
* NEXT - next page link
* LAST - 'got to last page' link which is not just a number
* FIRST - 'got to first page' link which is not just '1' number

Because LAST and FIRST are relatively rare they are converted to PAGE
by pagination model. By using these classes during annotation it can be
possible to make model predict them as well in future, with more training
examples.

To add a new page to training data save it to an html file
and add a row to the data.csv file. It is helpful
to use http://selectorgadget.com/ extension to get CSS selectors.

Don't worry if your CSS selectors don't return ``<a>`` elements directly
(it is easy to occasionally select a parent or a child of an ``<a>`` element
when using SelectorGadget). If a selection itself is not ``<a>`` element
then parent ``<a>`` elements and children ``<a>`` elements are tried, this is
usually what is wanted because ``<a>`` tags are not nested on valid websites.

When using SelectorGadget pay special attention not to select anything other
than pagination elements. Always check element count displayed by
SelectorGadget and compare it to a number of elements you wanted to select.

Some websites change their DOM after rendering. This rarely affect paginator
elements, but sometimes it can happen. To prevent it instead of downloading
HTML file using "Save As.." browser menu option it is better to use
"Copy Outer HTML" in developer tools or render HTML using a headless browser
(e.g. Splash_). If you do so make sure to put UTF-8 encoding to data.csv,
regardless of page encoding defined in HTTP headers or ``<meta>`` tags.

.. _Splash: https://github.com/scrapinghub/splash

----

.. image:: https://hyperiongray.s3.amazonaws.com/define-hg.svg
	:target: https://www.hyperiongray.com/?pk_campaign=github&pk_kwd=autopager
	:alt: define hyperiongray
