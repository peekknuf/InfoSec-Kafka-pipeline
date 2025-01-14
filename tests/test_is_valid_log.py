import unittest
from consumer.consumer import is_valid_log

class TestLogValidation(unittest.TestCase):
    def test_valid_log(self):
        log = "[2025-01-14T07:47:35+01:00] IP: 28.236.118.67, UserAgent: Mozilla/5.0, Message: Access denied"
        self.assertTrue(is_valid_log(log))

    def test_invalid_log(self):
        log = "Invalid log format"
        self.assertFalse(is_valid_log(log))

if __name__ == "__main__":
    unittest.main()
