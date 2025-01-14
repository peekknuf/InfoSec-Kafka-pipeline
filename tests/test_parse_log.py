import unittest
from consumer.consumer import parse_log

class TestLogParsing(unittest.TestCase):
    def test_valid_log(self):
        log = "[2025-01-14T07:47:35+01:00] IP: 28.236.118.67, UserAgent: Mozilla/5.0, Message: Access denied"
        expected = (
            "2025-01-14T07:47:35+01:00",
            "28.236.118.67",
            "Mozilla/5.0",
            "Access denied",
        )
        self.assertEqual(parse_log(log), expected)

    def test_invalid_log(self):
        log = "Invalid log format"
        self.assertIsNone(parse_log(log))

if __name__ == "__main__":
    unittest.main()
