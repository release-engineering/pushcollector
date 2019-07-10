import os
import datetime
import json
import logging

LOG = logging.getLogger("pushcollector")


class LocalCollector(object):
    # Registered as 'local' backend, this collector writes data to files under
    # the 'artifacts' subdir of the current working directory.
    # There is no way to customize the used directory.
    def __init__(self):
        self._artifacts_dir = os.path.join(os.getcwd(), "artifacts", self.timestamp())

    def update_push_items(self, items):
        with self._open_file("pushitems.jsonl", "a") as file:
            for item in items:
                json.dump(item, file, sort_keys=True)
                file.write("\n")

    def attach_file(self, filename, content):
        with self._open_file(filename, "wb") as file:
            file.write(content)

    def append_file(self, filename, content):
        with self._open_file(filename, "ab") as file:
            file.write(content)

    def _open_file(self, basename, *args, **kwargs):
        if not os.path.exists(self._artifacts_dir):
            os.makedirs(self._artifacts_dir)
            parent_dir = os.path.dirname(self._artifacts_dir)
            latest_link = os.path.join(parent_dir, "latest")
            if os.path.exists(latest_link):
                os.remove(latest_link)
            os.symlink(os.path.basename(self._artifacts_dir), latest_link)

        path = os.path.join(self._artifacts_dir, basename)

        # Log the first time we're creating each file
        if not os.path.exists(path):
            LOG.info("Logging to %s", path)

        return open(path, *args, **kwargs)

    @classmethod
    def timestamp(cls):
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")
