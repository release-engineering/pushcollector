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


def test_base_class_context_manager():
    """Exercise the __enter__ and __exit__ methods of Collector."""
    collector = Collector()
    # use my-collector name because the autouse fixture `reset_backend`
    # will clean it up for us
    Collector.register_backend("my-collector", lambda: collector)
    Collector.set_default_backend("my-collector")

    # empty with just to exercise __enter__ and __exit__
    with Collector.get():
        pass
