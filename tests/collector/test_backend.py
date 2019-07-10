import pytest

from pushcollector import Collector


@pytest.fixture(autouse=True)
def reset_backend():
    """Resets the default backend both before and after each test,
    and clears my-collector backend.
    """

    Collector.set_default_backend(None)
    yield
    Collector.set_default_backend(None)
    Collector.register_backend("my-collector", None)


def test_get_default():
    """Can get a default collector."""
    collector = Collector.get()
    assert collector


def test_set_default():
    """Can set and use a default collector."""

    class MyCollector(object):
        INSTANCES = []

        def __init__(self):
            MyCollector.INSTANCES.append(self)
            self.pushed = []

        def update_push_items(self, items):
            self.pushed.extend(items)

    Collector.register_backend("my-collector", MyCollector)
    Collector.set_default_backend("my-collector")

    items = [
        {"filename": "file1", "state": "PENDING"},
        {"filename": "file2", "state": "PENDING"},
    ]

    # Updating push items through default collector should succeed
    Collector.get().update_push_items(items).result()

    # It should have used the class we installed as the default
    assert len(MyCollector.INSTANCES) == 1
    assert MyCollector.INSTANCES[0].pushed == items


def test_register_backend_wrong_type():
    """register_backend raises TypeError if passed incorrect type"""

    with pytest.raises(TypeError):
        Collector.register_backend("my-colletor", Collector())


def test_get_missing():
    """Can't get a collector using unregistered backend."""
    with pytest.raises(ValueError) as excinfo:
        Collector.get("not-registered")
    value = excinfo.value
    assert "No registered pushcollector backend: 'not-registered'" in str(value)


def test_unregister_resets_default():
    """Unregistering a backend unsets it as the default backend (if it was set)."""

    class CountingCollector(object):
        CONSTRUCTED_COUNT = 0

        def __init__(self):
            CountingCollector.CONSTRUCTED_COUNT += 1

    Collector.register_backend("counter", CountingCollector)
    Collector.set_default_backend("counter")

    # Calling get() should construct custom backend once.
    Collector.get()
    assert CountingCollector.CONSTRUCTED_COUNT == 1

    # Calling get() should construct custom backend again.
    Collector.get()
    assert CountingCollector.CONSTRUCTED_COUNT == 2

    Collector.register_backend("counter", None)

    # Calling get() after unregister should succeed
    assert Collector.get()

    # And it should not have constructed the custom backend
    assert CountingCollector.CONSTRUCTED_COUNT == 2
