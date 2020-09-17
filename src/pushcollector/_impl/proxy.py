import os

import six
from more_executors.futures import f_return, f_map
import yaml
import jsonschema


def empty_future(value):
    if "add_done_callback" in dir(value):
        # It's a future, map it to None
        return f_map(value, lambda _: None)
    # It's not a future => operation has already completed,
    # return empty future to denote success
    return f_return()


def maybe_encode(value):
    if isinstance(value, six.text_type):
        # It's a string => make it bytes
        return value.encode("utf-8")
    # It's not a string => hopefully it's already bytes
    return value


def read_schema(filename):
    thisdir = os.path.dirname(__file__)
    path = os.path.join(thisdir, "schema", filename)
    with open(path) as schema_file:
        return yaml.safe_load(schema_file)


class CollectorProxy(object):
    # A proxy used to wrap any collector backend before providing to
    # the caller, i.e. this library does not return backend implementations
    # directly, it rather returns CollectorProxy(some_backend).
    #
    # This is done for a couple of reasons:
    #
    # - ensure backends cannot provide more than the documented API or
    #   have some differences from the documented API (e.g. default values
    #   for arguments)
    #
    # - implement certain Collector features here only once rather than
    #   requiring each backend to implement it.  Mainly, validation and
    #   coercion of arguments.
    #
    _ITEM_SCHEMA = read_schema("pushitem.yaml")

    def __init__(self, delegate):
        self._delegate = delegate

    def _translate_pushitem(self, pushitem):
        if isinstance(pushitem, dict):
            return [pushitem]

        pushitems = []
        checksums = {}
        if pushitem.md5sum:
            checksums["md5"] = pushitem.md5sum
        if pushitem.sha256sum:
            checksums["sha256"] = pushitem.sha256sum

        push_item = {
            "filename": pushitem.name,
            "state": pushitem.state,
            "src": pushitem.src,
            "dest": None,
            "checksums": checksums or None,
            "origin": pushitem.origin,
            "build": pushitem.build,
            "signing_key": pushitem.signing_key,
        }

        # a pushitem dict for each destination from the
        # list of destinations in PushItem object is
        # returned else a single pushitem with dest None
        # as expected in the pushitem schema
        for dest in pushitem.dest or []:
            push_item_copy = push_item.copy()
            push_item_copy["dest"] = dest
            pushitems.append(push_item_copy)

        return pushitems or [push_item]

    def update_push_items(self, items):
        pushitems = []
        for item in items:
            item_dicts = self._translate_pushitem(item)
            for item_dict in item_dicts:
                jsonschema.validate(item_dict, schema=self._ITEM_SCHEMA)
            pushitems.extend(item_dicts)

        return empty_future(self._delegate.update_push_items(pushitems))

    def attach_file(self, filename, content):
        content = maybe_encode(content)
        return empty_future(self._delegate.attach_file(filename, content))

    def append_file(self, filename, content):
        content = maybe_encode(content)
        return empty_future(self._delegate.append_file(filename, content))
