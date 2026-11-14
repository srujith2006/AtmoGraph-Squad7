"""Unit tests for structured JSON logging formatter and contextvars tracking."""

import json
import logging
import pytest
from src.core.logging import StructuredJSONFormatter, request_id_ctx


@pytest.mark.unit
def test_structured_json_formatter_standard_fields():
    """Verify JSON formatter outputs required observability fields."""
    formatter = StructuredJSONFormatter(service_name="atmograph-test")
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Test logging message",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)
    parsed = json.loads(formatted)

    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "test_logger"
    assert parsed["message"] == "Test logging message"
    assert parsed["service"] == "atmograph-test"
    assert "timestamp" in parsed
    assert "location" in parsed


@pytest.mark.unit
def test_structured_json_formatter_request_id_propagation():
    """Verify request_id from contextvar is included in log payload."""
    formatter = StructuredJSONFormatter()
    test_id = "req-12345-abcde"
    token = request_id_ctx.set(test_id)

    try:
        record = logging.LogRecord(
            name="test_logger",
            level=logging.WARNING,
            pathname=__file__,
            lineno=20,
            msg="Warning event with correlation",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        parsed = json.loads(formatted)

        assert parsed["request_id"] == test_id
    finally:
        request_id_ctx.reset(token)


@pytest.mark.unit
def test_structured_json_formatter_extra_metadata():
    """Verify custom attributes passed via extra are rendered in JSON."""
    formatter = StructuredJSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=30,
        msg="HTTP call",
        args=(),
        exc_info=None,
    )
    record.http_method = "POST"
    record.path = "/api/v1/nlp/ingest"
    record.status_code = 200
    record.duration_ms = 42.5

    formatted = formatter.format(record)
    parsed = json.loads(formatted)

    assert parsed["http_method"] == "POST"
    assert parsed["path"] == "/api/v1/nlp/ingest"
    assert parsed["status_code"] == 200
    assert parsed["duration_ms"] == 42.5


@pytest.mark.unit
def test_structured_json_formatter_exception_traceback():
    """Verify exception stack traces are serialized into an exception object."""
    formatter = StructuredJSONFormatter()
    try:
        raise ValueError("Simulated computation error")
    except ValueError:
        import sys
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname=__file__,
            lineno=45,
            msg="Exception caught",
            args=(),
            exc_info=sys.exc_info(),
        )

    formatted = formatter.format(record)
    parsed = json.loads(formatted)

    assert "exception" in parsed
    assert parsed["exception"]["type"] == "ValueError"
    assert "Simulated computation error" in parsed["exception"]["message"]
    assert isinstance(parsed["exception"]["stack_trace"], list)
