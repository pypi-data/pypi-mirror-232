import logging
import threading

import pytest
from utils import filter_gc

from picologging import INFO, Formatter, LogRecord, StrFormatStyle


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_strformatstyle():
    perc = StrFormatStyle("{msg} {levelno} {name}")
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    assert perc.format(record) == "hello 20 test"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_strformatstyle_from_formatter():
    perc = Formatter("{msg} {levelno} {name}", style="{")
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    assert perc.format(record) == "hello 20 test"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_strformatstyle_format_bad_argument():
    perc = StrFormatStyle("{msg} {levelno} {name}")
    with pytest.raises(AttributeError):
        perc.format(None)
    with pytest.raises(AttributeError):
        perc.format("")
    with pytest.raises(AttributeError):
        perc.format({})


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_custom_attribute():
    perc = StrFormatStyle("{custom}")
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    record.custom = "custom"
    assert perc.format(record) == "custom"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_strformatstyle_bad_init_args():
    with pytest.raises(TypeError):
        StrFormatStyle(dog="good boy")


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_funcname_format_string():
    perc = StrFormatStyle("{funcname}")
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, "superfunc", None)
    record.funcName = "superFunc"
    assert perc.format(record) == "superFunc"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_thread_id():
    perc = StrFormatStyle("{thread}")
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    assert record.thread == threading.get_ident()
    assert perc.format(record) == str(record.thread)


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_record_created():
    perc = StrFormatStyle("{created}")
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    assert perc.format(record) == str(record.created)


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_custom_field_not_an_attribute():
    perc = StrFormatStyle("{custom}")
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    with pytest.raises(AttributeError):
        assert perc.format(record)


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_strformatstyle_repr():
    perc = StrFormatStyle("{msg} {levelno} {name}")
    assert repr(perc) == "<FormatStyle fmt='{msg} {levelno} {name}' style='{'>"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_record_with_defaults():
    perc = StrFormatStyle(
        "{msg} {levelno} {name} {fruit}", defaults={"fruit": "banana"}
    )
    assert repr(perc) == "<FormatStyle fmt='{msg} {levelno} {name} {fruit}' style='{'>"
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    assert perc.format(record) == "hello 20 test banana"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_format_logging_record():
    perc = StrFormatStyle(
        "{msg} {levelno} {name} {fruit}", defaults={"fruit": "banana"}
    )
    record = logging.LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    assert perc.format(record) == "hello 20 test banana"
