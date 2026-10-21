import os
import sys
import threading
import unittest
from unittest.mock import patch

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "modules"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "tools"))

from main import AutoPlayBot


class FakeVision:
    def capture_screen(self):
        return object()

    def detect_cards(self, _img):
        return [object()] * 13


class FakeReader:
    def __init__(self, result):
        self.result = result

    def read_with_fallback(self, _img):
        return self.result


class SequenceReader:
    def __init__(self, results):
        self.results = iter(results)
        self.calls = 0

    def read_with_fallback(self, _img):
        self.calls += 1
        return next(self.results)


class FakeController:
    def __init__(self):
        self.pressed = []
        self.topups = []

    def press_key(self, action, delay=0.1):
        self.pressed.append(action)
        return True

    def auto_refill_credits(self, times):
        self.topups.append(times)
        return times


class MainFailClosedTests(unittest.TestCase):
    def make_bot(self, reader_result):
        bot = AutoPlayBot.__new__(AutoPlayBot)
        bot.vision = FakeVision()
        bot.safe_reader = FakeReader(reader_result)
        bot.controller = FakeController()
        bot.config = {"target_bet": 10}
        bot.stop_event = threading.Event()
        bot.running = True
        return bot

    def test_unknown_credit_or_bet_stops_without_inputs(self):
        for result in ((100, None, False),):
            with self.subTest(result=result):
                bot = self.make_bot(result)

                with patch("main.time.sleep"):
                    self.assertFalse(bot._prepare_round())
                self.assertFalse(bot.running)
                self.assertTrue(bot.stop_event.is_set())
                self.assertEqual(bot.controller.pressed, [])
                self.assertEqual(bot.controller.topups, [])

    def test_unknown_credit_sends_limited_topup_then_stops_on_unknown_bet(self):
        bot = self.make_bot((None, None, False))

        self.assertFalse(bot._prepare_round())

        self.assertEqual(bot.controller.topups, [15])
        self.assertEqual(bot.controller.pressed, [])
        self.assertFalse(bot.running)

    def test_known_target_bet_starts_only_after_reading_is_valid(self):
        bot = self.make_bot((100, 10, False))

        self.assertTrue(bot._prepare_round())
        self.assertEqual(bot.controller.pressed, ["START"])
        self.assertEqual(bot.controller.topups, [])
        self.assertTrue(bot.running)

    def test_low_credit_uses_limited_topup_without_score_recheck(self):
        bot = self.make_bot((5, 10, True))
        bot.safe_reader = SequenceReader([(5, 10, True)])

        with patch("main.time.sleep"):
            self.assertTrue(bot._prepare_round())

        self.assertEqual(bot.controller.topups, [15])
        self.assertEqual(bot.controller.pressed, ["START"])
        self.assertEqual(bot.safe_reader.calls, 1)
        self.assertTrue(bot.running)

    def test_unverified_bet_input_is_not_repeated(self):
        bot = self.make_bot((100, 0, False))
        bot.safe_reader = SequenceReader([(100, 0, False), (100, 0, False)])

        with patch("main.time.sleep"):
            self.assertFalse(bot._prepare_round())

        self.assertEqual(bot.controller.pressed, ["BET"])
        self.assertFalse(bot.running)


if __name__ == "__main__":
    unittest.main()
