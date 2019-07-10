import logging
import textwrap

from pushcollector import Collector


def test_local_saves_to_artifacts(caplog, tmpdir, monkeypatch):
    """local collector can be obtained and used successfully, and writes
    data under 'artifacts' dir as expected."""

    monkeypatch.chdir(tmpdir)

    caplog.set_level(logging.INFO)

    collector = Collector.get("local")

    collector.update_push_items(
        [
            {"filename": "file1", "state": "PUSHED"},
            {"filename": "file2", "state": "INVALIDFILE"},
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
            {"filename": "file2", "state": "INVALIDFILE"}
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
