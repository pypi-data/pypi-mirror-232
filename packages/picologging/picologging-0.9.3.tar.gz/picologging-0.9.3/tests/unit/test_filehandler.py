import os
import platform
import time
from datetime import datetime, timedelta

import pytest
from utils import filter_gc

import picologging
from picologging.handlers import (
    RotatingFileHandler,
    TimedRotatingFileHandler,
    WatchedFileHandler,
)


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_filehandler(tmp_path):
    log_file = tmp_path / "log.txt"
    handler = picologging.FileHandler(log_file)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)
    logger.warning("test")
    handler.close()

    with open(log_file) as f:
        assert f.read() == "test\n"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_filehandler_delay(tmp_path):
    log_file = tmp_path / "log.txt"
    handler = picologging.FileHandler(log_file, delay=True)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)
    logger.warning("test")
    handler.close()

    with open(log_file) as f:
        assert f.read() == "test\n"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
@pytest.mark.skipif(platform.system() == "Windows", reason="Not supported on Windows.")
def test_watchedfilehandler(tmp_path):
    log_file = tmp_path / "log.txt"
    handler = WatchedFileHandler(log_file)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)
    logger.warning("test")
    handler.close()

    with open(log_file) as f:
        assert f.read() == "test\n"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
@pytest.mark.skipif(platform.system() == "Windows", reason="Not supported on Windows.")
def test_watchedfilehandler_file_changed(tmp_path):
    log_file = tmp_path / "log.txt"
    handler = WatchedFileHandler(log_file)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)

    os.remove(log_file)
    with open(log_file, "w"):
        ...

    logger.warning("test")
    handler.close()

    with open(log_file) as f:
        assert f.read() == "test\n"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
@pytest.mark.skipif(platform.system() == "Windows", reason="Not supported on Windows.")
def test_watchedfilehandler_file_removed(tmp_path):
    log_file = tmp_path / "log.txt"
    handler = WatchedFileHandler(log_file)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)

    os.remove(log_file)

    logger.warning("test")
    handler.close()

    with open(log_file) as f:
        assert f.read() == "test\n"


@pytest.mark.limit_leaks("300B", filter_fn=filter_gc)
def test_rotatingfilehandler(tmp_path):
    log_file = tmp_path / "log.txt"
    handler = RotatingFileHandler(log_file, maxBytes=1, backupCount=2)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)

    for _ in range(5):
        logger.warning("test")
    handler.close()

    with open(log_file, encoding="utf-8") as f:
        assert f.read() == "test\n"

    for i in range(1, 3):
        log_file = tmp_path / f"log.txt.{i}"

        with open(log_file, encoding="utf-8") as f:
            assert f.read() == "test\n"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_rotatingfilehandler_avoids_non_regular_files(tmp_path, monkeypatch):
    log_file = tmp_path / "log.txt"
    handler = RotatingFileHandler(log_file, maxBytes=1, backupCount=2)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)

    logger.warning("test")

    monkeypatch.setattr(os.path, "isfile", lambda _: False)
    logger.warning("test")
    handler.close()


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_rotatingfilehandler_without_maxbytes(tmp_path):
    log_file = tmp_path / "log.txt"
    handler = RotatingFileHandler(log_file)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)

    logger.warning("test")
    handler.close()


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_baserotatinghandler_callable_rotator(tmp_path):
    log_file = tmp_path / "log.txt"
    handler = RotatingFileHandler(log_file, maxBytes=1, backupCount=1)
    handler.rotator = lambda src, dst: os.rename(src, dst)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)

    logger.warning("test")
    logger.warning("test")
    handler.close()
    assert sorted(os.listdir(tmp_path)) == ["log.txt", "log.txt.1"]


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_baserotatinghandler_callable_namer(tmp_path):
    log_file = tmp_path / "log.txt"
    handler = RotatingFileHandler(log_file, maxBytes=1, backupCount=1)
    handler.namer = lambda name: name + ".5"
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)

    logger.warning("test")
    logger.warning("test")
    handler.close()
    assert sorted(os.listdir(tmp_path)) == ["log.txt", "log.txt.1.5"]


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_filehandler_repr(tmp_path):
    log_file = tmp_path / "log.txt"
    handler = picologging.FileHandler(log_file)
    assert repr(handler) == f"<FileHandler {log_file} (NOTSET)>"
    handler.close()


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
@pytest.mark.parametrize("utc", [False, True])
def test_timed_rotatingfilehandler_rollover(tmp_path, utc):
    log_file = tmp_path / "log.txt"
    handler = TimedRotatingFileHandler(log_file, when="S", backupCount=1, utc=utc)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)

    logger.warning("test")
    handler.rollover_at = time.time() - 1

    logger.warning("test")
    handler.close()

    files = os.listdir(tmp_path)
    assert len(files) == 2

    for file_name in files:
        with open(tmp_path / file_name) as file:
            assert file.read() == "test\n"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_timed_rotatingfilehandler_rollover_removes_old_files(tmp_path):
    with open(tmp_path / "log.txt.1970-11-01_00-00-00", "w"):
        ...

    log_file = tmp_path / "log.txt"
    handler = TimedRotatingFileHandler(log_file, when="S", backupCount=1)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)

    logger.warning("test")
    handler.rollover_at = time.time() - 1
    logger.warning("test")
    handler.close()

    assert len(os.listdir(tmp_path)) == 2


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_timed_rotatingfilehandler_rollover_keeps_non_related_files(tmp_path):
    with open(tmp_path / "normal_file.txt", "w"):
        ...

    log_file = tmp_path / "log.txt"
    handler = TimedRotatingFileHandler(log_file, when="S", backupCount=1)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)

    logger.warning("test")
    handler.rollover_at = time.time() - 1
    logger.warning("test")
    handler.close()

    assert len(os.listdir(tmp_path)) == 3


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_timed_rotatingfilehandler_rollover_removes_existing_log(tmp_path, monkeypatch):
    existing_log_file = tmp_path / "log.txt.2022-07-01_16-00-00"
    with open(existing_log_file, "w"):
        ...

    log_file = tmp_path / "log.txt"
    handler = TimedRotatingFileHandler(log_file, when="S", backupCount=1)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)

    logger.warning("test")

    monkeypatch.setattr(handler, "rotation_filename", lambda _: existing_log_file)
    handler.rollover_at = time.time() - 1
    logger.warning("test")
    handler.close()

    assert len(os.listdir(tmp_path)) == 2


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_timed_rotatingfilehandler_non_existing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda _: False)

    log_file = tmp_path / "log.txt"
    handler = TimedRotatingFileHandler(log_file, when="S", backupCount=1)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)
    handler.close()


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_timed_rotatingfilehandler_when_intervals(tmp_path):
    when_interval = [
        ("S", 1),
        ("M", 60),
        ("H", 60 * 60),
        ("D", 60 * 60 * 24),
        ("MIDNIGHT", 60 * 60 * 24),
        ("W1", 60 * 60 * 24 * 7),
    ]

    log_file = tmp_path / "log.txt"
    for when, interval in when_interval:
        handler = TimedRotatingFileHandler(log_file, when=when)
        assert handler.interval == interval
        handler.close()


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_timed_rotatingfilehandler_invalid_when(tmp_path):
    log_file = tmp_path / "log.txt"

    with pytest.raises(ValueError):
        TimedRotatingFileHandler(log_file, when="W", delay=True)

    with pytest.raises(ValueError):
        TimedRotatingFileHandler(log_file, when="W7", delay=True)

    with pytest.raises(ValueError):
        TimedRotatingFileHandler(log_file, when="X", delay=True)


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_timed_rotatingfilehandler_utc(tmp_path):
    log_file = tmp_path / "log.txt"
    handler = TimedRotatingFileHandler(log_file, when="MIDNIGHT", utc=True)
    handler.close()
    assert handler.rollover_at > time.time()


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_timed_rotatingfilehandler_atime(tmp_path):
    log_file = tmp_path / "log.txt"
    at_time = (datetime.now() - timedelta(hours=1)).time()
    handler = TimedRotatingFileHandler(log_file, when="MIDNIGHT", atTime=at_time)
    handler.close()
    assert handler.rollover_at > time.time()


@pytest.mark.limit_leaks("200B", filter_fn=filter_gc)
def test_timed_rotatingfilehandler_avoids_non_regular_files(tmp_path, monkeypatch):
    log_file = tmp_path / "log.txt"
    handler = TimedRotatingFileHandler(log_file, backupCount=1)
    logger = picologging.getLogger("test")
    logger.setLevel(picologging.DEBUG)
    logger.addHandler(handler)

    logger.warning("test")

    monkeypatch.setattr(os.path, "isfile", lambda _: False)
    logger.warning("test")
    handler.close()
