import jsonschema
import pytest

from pushcollector import Collector


def test_bad_push_items():
    """Passing push items with incorrect data to update_push_items raises a
    validation error."""

    coll = Collector.get("dummy")

    with pytest.raises(jsonschema.ValidationError):
        coll.update_push_items([{"foo": "bar"}])
