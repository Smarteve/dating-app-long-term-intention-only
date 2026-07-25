import json
import logging

from app.core.logging import JsonFormatter, request_id_context


def test_json_formatter_adds_structured_context() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="profile_updated",
        args=(),
        exc_info=None,
    )
    record.account_id = "account-123"

    context_token = request_id_context.set("request-123")
    try:
        output = json.loads(formatter.format(record))
    finally:
        request_id_context.reset(context_token)

    assert output["level"] == "INFO"
    assert output["logger"] == "test"
    assert output["event"] == "profile_updated"
    assert output["request_id"] == "request-123"
    assert output["account_id"] == "account-123"
    assert "timestamp" in output
