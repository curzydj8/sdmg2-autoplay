"""Tests for safe credit top-up handling in the main game loop."""
import os
import sys
import threading
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "modules"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "tools"))

from main import AutoPlayBot


class FakeController:
    def __init__(self, sent_count):
        self.sent_count = sent_count
        self.calls = []

    def auto_refill_credits(self, times):
        self.calls.append(times)
        return self.sent_count


class TopUpFlowTests(unittest.TestCase):
    def make_bot(self, sent_count):
        bot = AutoPlayBot.__new__(AutoPlayBot)
        bot.controller = FakeController(sent_count)
        bot.stop_event = threading.Event()
        bot.running = True
        return bot

    def test_complete_topup_reports_dispatched_count_without_stopping(self):
        bot = self.make_bot(sent_count=5)

        self.assertTrue(bot._topup_credits(times=5))
        self.assertEqual(bot.controller.calls, [5])
        self.assertTrue(bot.running)
        self.assertFalse(bot.stop_event.is_set())

    def test_incomplete_topup_stops_the_bot(self):
        bot = self.make_bot(sent_count=3)

        self.assertFalse(bot._topup_credits(times=5))
        self.assertEqual(bot.controller.calls, [5])
        self.assertFalse(bot.running)
        self.assertTrue(bot.stop_event.is_set())


if __name__ == "__main__":
    unittest.main()
