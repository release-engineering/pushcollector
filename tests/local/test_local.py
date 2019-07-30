import logging
import textwrap

from pushcollector import Collector
from pushcollector._impl.local import LocalCollector


def test_local_saves_to_artifacts(caplog, tmpdir, monkeypatch):
    """local collector can be obtained and used successfully, and writes
    data under 'artifacts' dir as expected."""

    monkeypatch.chdir(tmpdir)

    caplog.set_level(logging.INFO)

    collector = Collector.get("local")

    collector.update_push_items(
        [
            {"filename": "file1", "state": "PUSHED"},
            {"filename": "somedir/file2", "state": "INVALIDFILE"},
        ]
    ).result()
    collector.update_push_items([{"filename": "file3", "state": "MISSING"}]).result()

    collector.attach_file("some-file.txt", u"Hello, world\n").result()
    collector.attach_file("some-file.txt", u"Hello again\n").result()
    collector.attach_file("some-file.bin", b"\x00\x01\x02").result()
    collector.append_file("appended-file.txt", u"chunk 1").result()
    collector.append_file("appended-file.txt", b"\nchunk 2\n").result()

    # It should have created an "artifacts/latest" directory/symlink
    artifactsdir = tmpdir.join("artifacts", "latest")
    assert artifactsdir.check(dir=True, link=True)

    # Resolve symlink for later comparison with log messages
    artifactsdir = artifactsdir.realpath()

    # It should have saved push item data as JSONL
    assert (
        artifactsdir.join("pushitems.jsonl").open().read()
        == textwrap.dedent(
            """
            {"filename": "file1", "state": "PUSHED"}
            {"filename": "somedir/file2", "state": "INVALIDFILE"}
            {"filename": "file3", "state": "MISSING"}
            """
        ).lstrip()
    )

    # It should have saved the text file with requested content
    assert artifactsdir.join("some-file.txt").open().read() == "Hello again\n"

    # It should have saved the binary file with requested content
    assert artifactsdir.join("some-file.bin").open("rb").read() == b"\x00\x01\x02"

    # It should have saved the appended-text file with requested content
    assert artifactsdir.join("appended-file.txt").open().read() == "chunk 1\nchunk 2\n"

    # It should have logged about the created files
    assert caplog.messages == [
        "Logging to %s" % artifactsdir.join("pushitems.jsonl"),
        "Logging to %s" % artifactsdir.join("some-file.txt"),
        "Logging to %s" % artifactsdir.join("some-file.bin"),
        "Logging to %s" % artifactsdir.join("appended-file.txt"),
    ]


def test_local_dir_sequence(tmpdir, monkeypatch):
    """local collector creates timestamped directories per run, with
    'latest' symlink pointing to latest"""
    monkeypatch.chdir(tmpdir)

    # Use first collector
    monkeypatch.setattr(LocalCollector, "timestamp", lambda cls: "time1")
    Collector.get("local").update_push_items(
        [{"filename": "file1", "state": "PUSHED"}]
    ).result()

    # Use another collector a few seconds later
    monkeypatch.setattr(LocalCollector, "timestamp", lambda cls: "time2")
    Collector.get("local").update_push_items(
        [{"filename": "file1", "state": "PUSHED"}]
    ).result()

    # And another even later
    monkeypatch.setattr(LocalCollector, "timestamp", lambda cls: "time3")
    Collector.get("local").update_push_items(
        [{"filename": "file1", "state": "PUSHED"}]
    ).result()

    # It should have created these paths:
    artifactsdir = tmpdir.join("artifacts")
    assert artifactsdir.check(dir=True)
    assert artifactsdir.join("time1").check(dir=True)
    assert artifactsdir.join("time2").check(dir=True)
    assert artifactsdir.join("time3").check(dir=True)
    assert artifactsdir.join("latest").check(dir=True, link=True)

    # and latest should be a symlink to the last created timestamp dir
    assert artifactsdir.join("latest").readlink() == "time3"
