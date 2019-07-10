.. _backends:

Backends
========

The pushcollector library ships with multiple backends implementing the
:class:`~pushcollector.Collector` interface, and also allows integrators
to implement and register their own backends.

.. contents::
  :local:

local
-----

The "local" backend is the default backend for the pushcollector library.

.. code-block:: python

    Collector.get("local")

This backend collects all recorded information into an ``artifacts`` directory
under the current working directory (at the time the collector was initialized).

Timestamped subdirectories are used so that commands using this backend will
write to a new subdirectory on each run, while a 'latest' symlink is written to
make it easy to identify the most recent artifacts directory.

Here is an example of the directory structure created by this backend:

.. code-block::

  $ tree artifacts
  artifacts
  └── 20190710143228
  │   ├── attached-file1.txt
  │   ├── attached-file2.bin
  │   └── pushitems.jsonl
  └── latest -> 20190710143228

  2 directory, 3 files

The timestamped artifacts subdirectory will contain:

* ``pushitems.jsonl``, a file in `JSON Lines`_ format.
  Each line in the file is a single push item, using the defined :ref:`schema`.
* Any other files attached via :meth:`~pushcollector.Collector.attach_file`
  or  :meth:`~pushcollector.Collector.append_file`.

dummy
-----

The "dummy" backend ignores all provided data.

.. code-block:: python

    Collector.get("dummy")

This backend may be useful in automated tests and other environments
where there is no need to collect information during a task.

Note that, even when the dummy backend is in use, all push item data
provided to the backend must satisfy the :ref:`schema`.


Implementing a backend
----------------------

The built-in backends are intended for local development and testing.
For production use, you'll likely need to implement your own backend
suitable for your task execution environment.  These are the
necessary steps to add a new backend:


Implement collector interface
.............................

Write a class which implements the instance methods on
the :class:`~pushcollector.Collector` interface. This class should
do whatever's needed to record push items and log files in your
environment (e.g. inserting records to a database; copying log files
to a remote host).

Here is an example of a contrived collector backend which saves push items
to a database, and sends attached "files" to :mod:`syslog`.

.. code-block:: python

  class MyCollector:
    def __init__(self, db):
      self.db = db

    def update_push_items(self, items):
      for item in items:
        self.db.upsert(item)

    def attach_file(self, filename, content):
      try:
        syslog.openlog(filename)
        syslog.syslog(content)
      finally:
        syslog.closelog()

    def append_file(self, filename, content):
      return self.attach_file(filename, content)

When implementing a collector backend, take note of the following:

- All push items are automatically validated against the :ref:`schema`,
  so it's unnecessary to repeat this validation in your backend.

- Your ``update_push_items`` implementation should be prepared to accept
  anywhere from zero to tens of thousands of items at once, so the backend
  may have to consider scaling and performance issues.

- The ``attach_file`` and ``append_file`` methods are always invoked with
  content encoded as :class:`bytes`; backends shouldn't attempt to handle
  encoding themselves.

- Although the :class:`~pushcollector.Collector` interface is defined as
  returning :class:`~concurrent.futures.Future` instances, your backend is allowed
  to be implemented in a blocking or non-blocking style. If implemented as
  fully blocking, it need not return futures (as in the above example).


Register the backend
....................

Call the :meth:`~pushcollector.Collector.register_backend` method to register
the backend with the library, using a short meaningful name.

This method accepts any callable which can be invoked to create an instance
of your backend.  If your backend can be constructed with no arguments, this
could be simply the name of the class you've implemented:

.. code-block:: python

  Collector.register_backend('my-collector', MyCollector)

Alternatively, if you need to pass some context into your backend, you could
bind that context when the backend is registered.

.. code-block:: python

  Collector.register_backend('my-collector', lambda: MyCollector(db=some_database))


Set as default (optional)
.........................

After you've registered your own backend, you can optionally set it as the default
backend for the library. This is useful in order to provide your backend to third-party
code implemented against the default backend.

Use the  :meth:`~pushcollector.Collector.set_default_backend` method to achieve this:

.. code-block:: python

  Collector.set_default_backend('my-collector')


Unregister backend (optional)
.............................

If it's not appropriate for your backend to remain available for the lifetime
of the current process, you can unregister it once it's no longer required.
Simply call the :meth:`~pushcollector.Collector.register_backend` method again,
passing ``None`` as the value for your backend.

Unregistering a backend also unsets the backend as the library's default.

.. code-block:: python

  Collector.register_backend('my-collector', None)
  # my-collector backend is now unavailable


.. _JSON Lines: http://jsonlines.org/
