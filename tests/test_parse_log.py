import logging
import pytest
from src.consumer.consumer import parse_log

VALID_LOG = (
    "2025-01-18T19:05:00.830128259+01:00 | ACT-20250118T190500-140 | SUSPICIOUS_LOGIN_ATTEMPT | "
    "user_id=u-286259 username= ip_address=83.21.115.122 country= region= city= coordinates=-75.2494,15.4804 "
    "os=macOS 12 browser=Firefox 118.0.0.0 device_type=Tablet | action=PASSWORD_CHANGE status=FAILED | "
    "session_id=sess-327525 request_id=req-355181924 trace_id=trace-c5879fea3795"
)

# Expected output for the valid log
EXPECTED_OUTPUT = (
    "2025-01-18T19:05:00.830128259+01:00",  # timestamp
    "ACT-20250118T190500-140",  # log_id
    "SUSPICIOUS_LOGIN_ATTEMPT",  # event_type
    "u-286259",  # user_id
    None,  # username (empty → None)
    "83.21.115.122",  # ip_address
    None,  # country (empty → None)
    None,  # region (empty → None)
    None,  # city (empty → None)
    "-75.2494,15.4804",  # coordinates
    "macOS 12",  # os
    "Firefox 118.0.0.0",  # browser
    "Tablet",  # device_type
    "PASSWORD_CHANGE",  # action
    "FAILED",  # status
    "sess-327525",  # session_id
    "req-355181924",  # request_id
    "trace-c5879fea3795",  # trace_id
)

# Invalid log examples
INVALID_LOGS = [
    "",  # Empty log
    "2025-01-18T19:05:00.830128259+01:00 | ACT-20250118T190500-140",  # Incomplete log
    "2025-01-18T19:05:00.830128259+01:00 | ACT-20250118T190500-140 | SUSPICIOUS_LOGIN_ATTEMPT",  # Missing fields
    "2025-01-18T19:05:00.830128259+01:00 | ACT-20250118T190500-140 | SUSPICIOUS_LOGIN_ATTEMPT | user_id=u-286259",  # Partial fields
]


def test_parse_log_valid():
    """Test that a valid log is parsed correctly."""
    result = parse_log(VALID_LOG)
    assert result == EXPECTED_OUTPUT, f"Expected {EXPECTED_OUTPUT}, got {result}"


def test_parse_log_invalid():
    """Test that invalid logs return None."""
    for log in INVALID_LOGS:
        result = parse_log(log)
        assert result is None, f"Expected None for invalid log, got {result}"


def test_parse_log_edge_cases():
    """Test edge cases for log parsing."""
    # Log with missing optional fields
    log_missing_optional = (
        "2025-01-18T19:05:00.830128259+01:00 | ACT-20250118T190500-140 | SUSPICIOUS_LOGIN_ATTEMPT | "
        "user_id=u-286259 username= ip_address=83.21.115.122 country= region= city= coordinates= "
        "os= browser= device_type= | action= status= | session_id= request_id= trace_id="
    )
    expected_missing_optional = (
        "2025-01-18T19:05:00.830128259+01:00",  # timestamp
        "ACT-20250118T190500-140",  # log_id
        "SUSPICIOUS_LOGIN_ATTEMPT",  # event_type
        "u-286259",  # user_id
        None,  # username (empty → None)
        "83.21.115.122",  # ip_address
        None,  # country (empty → None)
        None,  # region (empty → None)
        None,  # city (empty → None)
        None,  # coordinates (empty → None)
        None,  # os (empty → None)
        None,  # browser (empty → None)
        None,  # device_type (empty → None)
        None,  # action (empty → None)
        None,  # status (empty → None)
        None,  # session_id (empty → None)
        None,  # request_id (empty → None)
        None,  # trace_id (empty → None)
    )
    result = parse_log(log_missing_optional)
    assert result == expected_missing_optional, (
        f"Expected {expected_missing_optional}, got {result}"
    )

    # Log with extra fields (should still parse correctly)
    log_extra_fields = (
        "2025-01-18T19:05:00.830128259+01:00 | ACT-20250118T190500-140 | SUSPICIOUS_LOGIN_ATTEMPT | "
        "user_id=u-286259 username= ip_address=83.21.115.122 country= region= city= coordinates=-75.2494,15.4804 "
        "os=macOS 12 browser=Firefox 118.0.0.0 device_type=Tablet | action=PASSWORD_CHANGE status=FAILED | "
        "session_id=sess-327525 request_id=req-355181924 trace_id=trace-c5879fea3795 extra_field=extra_value"
    )
    result = parse_log(log_extra_fields)
    assert result == EXPECTED_OUTPUT, f"Expected {EXPECTED_OUTPUT}, got {result}"


def test_parse_log_warning(caplog):
    """Test that invalid logs trigger a warning."""
    invalid_log = "invalid log format"
    with caplog.at_level(logging.WARNING):
        parse_log(invalid_log)
    assert "Log format is invalid" in caplog.text, (
        "Expected a warning for invalid log format"
    )
