import logging
import threading

import pytest
from utils import filter_gc

from picologging import INFO, LogRecord, PercentStyle


@pytest.mark.limit_leaks("168B", filter_fn=filter_gc)
def test_percentstyle():
    perc = PercentStyle("%(msg)s %(levelno)d %(name)s")
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    assert perc.format(record) == "hello 20 test"


@pytest.mark.limit_leaks("225B", filter_fn=filter_gc)
def test_percentstyle_format_bad_argument():
    perc = PercentStyle("%(msg)s %(levelno)d %(name)s")
    with pytest.raises(AttributeError):
        perc.format(None)
    with pytest.raises(AttributeError):
        perc.format("")
    with pytest.raises(AttributeError):
        perc.format({})


@pytest.mark.limit_leaks("223B", filter_fn=filter_gc)
def test_custom_attribute():
    perc = PercentStyle("%(custom)s")
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    record.custom = "custom"
    assert perc.format(record) == "custom"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_percentstyle_bad_init_args():
    with pytest.raises(TypeError):
        PercentStyle(dog="good boy")


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_funcname_format_string():
    perc = PercentStyle("%(funcname)s")
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, "superfunc", None)
    record.funcName = "superFunc"
    assert perc.format(record) == "superFunc"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_thread_id():
    perc = PercentStyle("%(thread)d")
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    assert record.thread == threading.get_ident()
    assert perc.format(record) == str(record.thread)


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_record_created():
    perc = PercentStyle("%(created)f")
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    assert perc.format(record) == str(record.created)


def test_custom_field_not_an_attribute():
    perc = PercentStyle("%(custom)s")
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    with pytest.raises(AttributeError):
        assert perc.format(record)


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_percentstyle_repr():
    perc = PercentStyle("%(msg)s %(levelno)d %(name)s")
    assert repr(perc) == "<FormatStyle fmt='%(msg)s %(levelno)d %(name)s' style='%'>"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_record_with_defaults():
    perc = PercentStyle(
        "%(msg)s %(levelno)d %(name)s %(fruit)s", defaults={"fruit": "banana"}
    )
    record = LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    assert perc.format(record) == "hello 20 test banana"


@pytest.mark.limit_leaks("192B", filter_fn=filter_gc)
def test_format_logging_record():
    perc = PercentStyle(
        "%(msg)s %(levelno)d %(name)s %(fruit)s", defaults={"fruit": "banana"}
    )
    record = logging.LogRecord("test", INFO, __file__, 1, "hello", (), None, None, None)
    assert perc.format(record) == "hello 20 test banana"
