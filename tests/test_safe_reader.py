import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "modules"))

from safe_reader import SafeCreditBetReader


class UnknownVision:
    def read_credit_bet(self, _img):
        return (None, None)


class SafeReaderTests(unittest.TestCase):
    def test_repeated_unknown_reads_never_request_topup(self):
        reader = SafeCreditBetReader(UnknownVision())
        reader._ocr_credit = lambda _img: None

        first = reader.read_with_fallback(object())
        second = reader.read_with_fallback(object())

        self.assertEqual(first, (None, None, False))
        self.assertEqual(second, (None, None, False))
        self.assertEqual(reader.consecutive_failures, 2)


if __name__ == "__main__":
    unittest.main()
