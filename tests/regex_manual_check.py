import re

log_pattern = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+-]\d{2}:\d{2}) \| "
    r"(?P<log_id>ACT-\d{8}T\d{6}-\d+) \| "
    r"(?P<event_type>[A-Z_]+) \| "
    r"user_id=(?P<user_id>[^\s]+) "
    r"username=(?P<username>[^|]*?) "
    r"ip_address=(?P<ip_address>[^\s]+) "
    r"country=(?P<country>[^|]*?) "
    r"region=(?P<region>[^|]*?) "
    r"city=(?P<city>[^|]*?) "
    r"coordinates=(?P<coordinates>[^|]*?) "
    r"os=(?P<os>[^|]*?) "
    r"browser=(?P<browser>[^|]*?) "
    r"device_type=(?P<device_type>[^|]*?) \| "
    r"action=(?P<action>[^\s]+) "
    r"status=(?P<status>[^\s]+) \| "
    r"session_id=(?P<session_id>[^\s]+) "
    r"request_id=(?P<request_id>[^\s]+) "
    r"trace_id=(?P<trace_id>[^\s]+)"
)

log_message = (
    "2025-01-18T19:05:00.830128259+01:00 | ACT-20250118T190500-140 | SUSPICIOUS_LOGIN_ATTEMPT | "
    "user_id=u-286259 username= ip_address=83.21.115.122 country= region= city= coordinates=-75.2494,15.4804 "
    "os=macOS 12 browser=Firefox 118.0.0.0 device_type=Tablet | action=PASSWORD_CHANGE status=FAILED | "
    "session_id=sess-327525 request_id=req-355181924 trace_id=trace-c5879fea3795"
)

match = log_pattern.match(log_message)
if match:
    print("Regex matched successfully!")
    print(match.groupdict())
else:
    print("Regex did not match the log.")
