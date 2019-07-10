pushcollector
=============

A Python library for collecting information from push tasks, used by
[release-engineering](https://github.com/release-engineering) publishing tools.

[![Build Status](https://travis-ci.org/release-engineering/pushcollector.svg?branch=master)](https://travis-ci.org/release-engineering/pushcollector)
[![Coverage Status](https://coveralls.io/repos/github/release-engineering/pushcollector/badge.svg?branch=master)](https://coveralls.io/github/release-engineering/pushcollector?branch=master)

- [Source](https://github.com/release-engineering/pushcollector)
- [Documentation](https://release-engineering.github.io/pushcollector/)
- [PyPI](https://pypi.org/project/pushcollector)


Installation
------------

Install the `pushcollector` package from PyPI.

```
pip install pushcollector
```


Usage Example
-------------

```python
from pushcollector import Collector

# Get an instance of a collector; the concrete backend returned
# may differ per execution environment
collector = Collector.get()

# Save a log file
collector.attach_file('pushlog.json', json.dumps(somedata)).result()

# Append to a log file
collector.append_file('pushlog.txt', sometext).result()

# Save some push item(s)
collector.update_push_items(items).result()
```

Development
-----------

Patches may be contributed via pull requests to
https://github.com/release-engineering/pushcollector.

All changes must pass the automated test suite, along with various static
checks.

The [Black](https://black.readthedocs.io/) code style is enforced.
Enabling autoformatting via a pre-commit hook is recommended:

```
pip install -r requirements-dev.txt
pre-commit install
```

License
-------

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
