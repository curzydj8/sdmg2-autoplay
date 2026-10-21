"""Regression tests for arcade digit template recognition."""
import os
import sys
import unittest

import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "modules"))

from vision import ArcadeDigitMatcher


class ArcadeDigitMatcherTests(unittest.TestCase):
    def test_recognize_imports_cv2_before_processing_nonuniform_roi(self):
        matcher = ArcadeDigitMatcher(
            os.path.join(PROJECT_ROOT, "templates", "digits")
        )
        matcher.segment_digits = lambda roi: []
        roi = np.zeros((20, 20, 3), dtype=np.uint8)
        roi[5:15, 5:15] = 255

        self.assertIsNone(matcher.recognize(roi, "bet"))


if __name__ == "__main__":
    unittest.main()
