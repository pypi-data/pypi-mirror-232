import copy
import logging
import os
import threading

import pytest
from utils import filter_gc

import picologging
from picologging import LogRecord


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_logrecord_standard():
    record = LogRecord(
        "hello", logging.WARNING, __file__, 123, "bork bork bork", (), None
    )
    assert record.name == "hello"
    assert record.msg == "bork bork bork"
    assert record.levelno == logging.WARNING
    assert record.levelname == "WARNING"
    assert record.pathname == __file__
    assert record.module == "test_logrecord"
    assert record.filename == "test_logrecord.py"
    assert record.args == ()
    assert record.created


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_logrecord_args():
    record = LogRecord(
        "hello", logging.WARNING, __file__, 123, "bork %s", ("boom"), None
    )
    assert record.name == "hello"
    assert record.msg == "bork %s"
    assert record.args == ("boom")
    assert record.message is None


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_logrecord_getmessage_with_args():
    record = LogRecord(
        "hello", logging.WARNING, __file__, 123, "bork %s", ("boom"), None
    )
    assert record.message is None
    assert record.getMessage() == "bork boom"
    assert record.message == "bork boom"
    assert record.message == "bork boom"


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_logrecord_getmessage_no_args():
    record = LogRecord("hello", logging.WARNING, __file__, 123, "bork boom", (), None)
    assert record.message is None
    assert record.getMessage() == "bork boom"
    assert record.message == "bork boom"
    assert record.message == "bork boom"


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_args_format_mismatch():
    record = LogRecord(
        "hello", logging.WARNING, __file__, 123, "bork boom %s %s", (0,), None
    )
    assert record.message is None
    with pytest.raises(TypeError):
        record.getMessage()


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_args_len_mismatch():
    record = LogRecord(
        "hello", logging.WARNING, __file__, 123, "bork boom %s", (0, 1, 2), None
    )
    assert record.message is None
    with pytest.raises(TypeError):
        record.getMessage()


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_no_args():
    record = LogRecord("hello", logging.WARNING, __file__, 123, "bork boom", None, None)
    assert record.message is None
    assert record.getMessage() == "bork boom"
    assert record.message == "bork boom"


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_no_args_and_format():
    record = LogRecord("hello", logging.WARNING, __file__, 123, "bork %s", None, None)
    assert record.message is None
    assert record.getMessage() == "bork %s"
    assert record.message == "bork %s"


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_logrecord_single_string_arg():
    record = LogRecord("", picologging.WARNING, "", 12, " %s", "\U000b6fb2", None)
    assert record.args == "\U000b6fb2"
    assert record.getMessage() == " \U000b6fb2"


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_logrecord_single_empty_string_in_tuple_arg():
    record = LogRecord("", 0, "", 0, " %s", ("",), None)
    assert record.args == ("",)
    assert record.getMessage() == " "


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_logrecord_single_dict_in_tuple_arg():
    record = LogRecord("", 0, "", 0, "%(key)s", ({"key": "val"},), None)
    assert record.args == {"key": "val"}
    assert record.getMessage() == "val"


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_logrecord_nested_tuple_arg():
    record = LogRecord("", 0, "", 0, "%d %s", ((10, "bananas"),), None)
    assert record.args == ((10, "bananas"),)
    with pytest.raises(TypeError):
        record.getMessage()


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_repr():
    record = LogRecord("hello", logging.WARNING, __file__, 123, "bork %s", (0,), None)
    assert repr(record) == f"<LogRecord: hello, 30, {__file__}, 123, 'bork %s'>"


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_mapping_dict():
    args = {
        "a": "b",
    }
    record = LogRecord(
        "hello", logging.WARNING, __file__, 123, "bork %s", (args,), None
    )
    assert record.args == {"a": "b"}


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_threading_info():
    record = LogRecord("hello", logging.WARNING, __file__, 123, "bork", (), None)
    assert record.thread == threading.get_ident()
    assert record.threadName is None  # Not supported


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_process_info():
    record = LogRecord("hello", logging.WARNING, __file__, 123, "bork", (), None)
    assert record.process == os.getpid()
    assert record.processName is None  # Not supported


@pytest.mark.limit_leaks("1.5KB", filter_fn=filter_gc)
def test_logrecord_subclass():
    class DerivedLogRecord(LogRecord):  # Leaks 1 ref (CPython implementation detail)
        pass

    record = DerivedLogRecord(
        "hello", logging.WARNING, __file__, 123, "bork boom", (), None
    )

    assert DerivedLogRecord.__base__ is LogRecord
    assert record.message is None
    assert record.getMessage() == "bork boom"
    assert record.message == "bork boom"
    assert record.message == "bork boom"

    handler = picologging.StreamHandler()
    handler.emit(record)


@pytest.mark.limit_leaks("512B", filter_fn=filter_gc)
def test_logrecord_copy():
    record = LogRecord("hello", logging.WARNING, __file__, 123, "bork boom", (), None)
    copied_record = copy.copy(record)

    assert copied_record.name == record.name
    assert copied_record.levelno == record.levelno
    assert copied_record.levelname == record.levelname
    assert copied_record.pathname == record.pathname
    assert copied_record.lineno == record.lineno
    assert copied_record.msg == record.msg
    assert copied_record.message == record.message
    assert copied_record.args == record.args
    assert copied_record.exc_info == record.exc_info
    assert copied_record.funcName == record.funcName
    assert copied_record.stack_info == record.stack_info
