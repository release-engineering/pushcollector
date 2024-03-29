import jsonschema
import pytest
from mock import Mock

from pushsource import PushItem

from pushcollector import Collector


def test_bad_push_items():
    """Passing push items with incorrect data to update_push_items raises a
    validation error."""

    coll = Collector.get("dummy")

    with pytest.raises(jsonschema.ValidationError):
        coll.update_push_items([{"foo": "bar"}])


def test_pushitem_obj_push():
    """PushItem object passed to the update_push_items works fine."""

    collector = Collector.get("dummy")

    pushitem = PushItem(name="test_pushitem")
    ret_val = collector.update_push_items([pushitem])

    assert ret_val.result() is None


def test_bad_obj_push():
    """Any invalid object type push item raises an error."""

    collector = Collector.get("dummy")

    pushitem = object()
    with pytest.raises(AttributeError):
        collector.update_push_items([pushitem])


def test_pushitem_obj_attributes():
    """PushItem object attributes are translated and available as expected in
    pushitem dict passed to update_push_items. A pushitem is generated for each
    destination"""

    mock = Mock()
    Collector.register_backend("mock", lambda: mock)
    collector = Collector.get("mock")

    pushitem = PushItem(
        name="test_push",
        origin="some_origin",
        src="source",
        dest=["dest1", "dest2"],
        md5sum="bb1b0d528129f47798006e73307ba7a7",
        sha256sum="4fd23ae44f3366f12f769f82398e96dce72adab8e45dea4d721ddf43fdce31e2",
        build="test_build-1.0.0-1",
        signing_key="FD431D51",
    )
    collector.update_push_items([pushitem])

    update_push_item_args = mock.update_push_items.call_args[0][0]
    assert len(update_push_item_args) == 2
    for i in range(len(update_push_item_args) - 1):
        push_args = update_push_item_args[i]
        assert push_args["filename"] == pushitem.name
        assert push_args["state"] == pushitem.state
        assert push_args["src"] == pushitem.src
        assert push_args["dest"] == pushitem.dest[i]
        assert push_args["checksums"] == {
            "md5": pushitem.md5sum,
            "sha256": pushitem.sha256sum,
        }
        assert push_args["origin"] == pushitem.origin
        assert push_args["build"] == pushitem.build
        assert push_args["signing_key"] == pushitem.signing_key


def test_minimal_pushitem_obj():
    """PushItem object with minimal attributes is translated to
    pushitem dict with destination and checksums as None along
    with other attributes as in the object"""

    mock = Mock()
    Collector.register_backend("mock", lambda: mock)
    collector = Collector.get("mock")

    pushitem = PushItem(name="test_push")
    collector.update_push_items([pushitem])

    update_push_item_args = mock.update_push_items.call_args[0][0]
    assert len(update_push_item_args) == 1
    push_args = update_push_item_args[0]
    assert push_args["filename"] == pushitem.name
    assert push_args["state"] == pushitem.state
    assert push_args["src"] == pushitem.src
    assert push_args["dest"] is None
    assert push_args["checksums"] is None
    assert push_args["origin"] == pushitem.origin
    assert push_args["build"] == pushitem.build
    assert push_args["signing_key"] == pushitem.signing_key
