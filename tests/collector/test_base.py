import pytest

from pushcollector import Collector


def test_unimplemented():
    """Collector base class raises NotImplementedError for all public API."""
    collector = Collector()

    with pytest.raises(NotImplementedError):
        collector.update_push_items([])

    with pytest.raises(NotImplementedError):
        collector.attach_file("somefile.txt", "foobar")

    with pytest.raises(NotImplementedError):
        collector.append_file("somefile.txt", "foobar")
