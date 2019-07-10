from pushcollector import Collector


def test_can_use_dummy():
    """Dummy collector can be obtained and used successfully."""

    coll = Collector.get("dummy")

    coll.update_push_items(
        [
            {"filename": "file1", "state": "PUSHED"},
            {"filename": "file2", "state": "UNKNOWN"},
        ]
    ).result()

    coll.attach_file("somefile.txt", "hello, world").result()
    coll.append_file("otherfile.txt", "line of text\n").result()
