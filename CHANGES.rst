Changes
=======

0.4.0 (TBD)
-----------

* Minimum Python requirement is now 3.8
* Dropped Python 2 support
* Removed `six` dependency - using native Python 3 features
* Removed `from __future__` imports (not needed in Python 3)
* Removed `# -*- coding: utf-8 -*-` headers (default in Python 3)
* Replaced `io.open` with built-in `open`
* Fixed regex warnings by using raw strings
* Updated CI to test Python 3.8-3.12

0.3.1 (2020-09-09)
------------------

* Fixing the distribution;
* backports.csv is no longer required in setup.py

0.3 (2020-09-09)
----------------

* Minimum Python requirement is now 3.6. Older versions may still work,
  but they're no longer tested on CI.
* Memory usage is limited, to avoid spikes on pathological pages.

0.2 (2016-04-26)
----------------

* more training examples;
* fixed Scrapy < 1.1 support;
* fixed a bug in text-before and text-after features.

0.1 (2016-03-15)
----------------

Initial release
