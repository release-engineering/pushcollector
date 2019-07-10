pushcollector
=============

A library for collecting information from push tasks.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api-reference
   backends
   schema

Quick Start
-----------

Install pushcollector from PyPI:

::

    pip install pushcollector

In your python code, obtain a :class:`~pushcollector.Collector` instance and use it
to record information about a task as it runs:

.. code-block:: python

    import sys
    from concurrent import futures
    from pushcollector import Collector

    collector = Collector.get()

    fs = []
    items = []
    for filename in sys.argv[1:]:
        try:
            upload_file(filename)
            items.append({"filename": filename, "state": "PUSHED"})
        except Exception as exc:
            log.exception("Error handling %s", filename)
            items.append({"filename": filename, "state": "UPLOADFAILED"})
            fs.append(collector.append_file('error.log', str(exc)))

    fs.append(collector.update_push_items(items))

    # Wait for the collector to finish all work
    futures.wait(fs)

The :class:`~pushcollector.Collector` class will record data using the configured
backend. pushcollector provides a couple of simple backends, but it will often be
necessary to implement a custom backend appropriate for your task execution
environment.  See :ref:`backends` for more information about available backends and
implementing your own backend.
