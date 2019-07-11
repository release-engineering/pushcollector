import jsonschema
import pytest
from more_executors.futures import f_return, f_return_error

from pushcollector import Collector


def test_always_returns_future():
    """Collector interface returns futures regardless of backend return type."""

    return_value = None

    class TestCollector(object):
        def update_push_items(self, items):
            return return_value

        def attach_file(self, filename, content):
            return return_value

        def append_file(self, filename, content):
            return return_value

    Collector.register_backend("test", TestCollector)
    collector = Collector.get("test")

    # If backend returns a successful future (of any value),
    # interface returns an empty future
    return_value = f_return("abc")
    assert collector.update_push_items([]).result() is None
    assert collector.attach_file("somefile", "").result() is None
    assert collector.append_file("somefile", "").result() is None

    # If backend returns a failed future,
    # interface returns a failed future with error propagated
    error = RuntimeError("oops")
    return_value = f_return_error(error)
    assert collector.update_push_items([]).exception() is error
    assert collector.attach_file("somefile", "").exception() is error
    assert collector.append_file("somefile", "").exception() is error

    # If backend returns a non-future,
    # interface returns an empty future
    return_value = "abc"
    assert collector.update_push_items([]).result() is None
    assert collector.attach_file("somefile", "").result() is None
    assert collector.append_file("somefile", "").result() is None
