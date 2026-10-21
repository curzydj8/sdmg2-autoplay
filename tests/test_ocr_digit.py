"""Tests for the isolated Tesseract digit-recognition experiment."""
import os
import sys
from unittest.mock import patch

import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "modules"))

from ocr_digit import OCRDigitReader


def test_zero_confidence_returns_unknown_and_preserves_diagnostics():
    reader = OCRDigitReader()
    reader.available = True
    roi = np.zeros((20, 30, 3), dtype=np.uint8)
    roi[5:15, 10:20] = 255
    ocr_data = {"text": ["1"], "conf": ["0"]}

    with patch("pytesseract.image_to_data", return_value=ocr_data):
        text, confidence, debug = reader.read(roi)

    assert text is None
    assert confidence == 0.0
    assert debug["raw_text"] == "1"
    assert debug["reason"] == "置信度低(0.0)"


def test_missing_pytesseract_returns_unknown():
    reader = OCRDigitReader()
    reader.available = False

    text, confidence, debug = reader.read(np.zeros((20, 30, 3), dtype=np.uint8))

    assert text is None
    assert confidence == 0.0
    assert debug["reason"] == "pytesseract未安装"


if __name__ == "__main__":
    test_zero_confidence_returns_unknown_and_preserves_diagnostics()
    test_missing_pytesseract_returns_unknown()
    print("OCR digit tests passed")
