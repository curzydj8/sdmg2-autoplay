import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "modules"))

from controls import E, KEY_MAP


class ControlsKeymapTests(unittest.TestCase):
    def test_mame_function_and_system_keys(self):
        expected = {
            "TAKE_SCORE": E.KEY_RIGHTCTRL,
            "LAST_CHANCE": E.KEY_RIGHTALT,
            "PAYOUT": E.KEY_4,
            "SHOW_CREDITS": E.KEY_9,
            "BOOK_KEEPING": E.KEY_0,
            "SERVICE_3": E.KEY_MINUS,
            "SERVICE_MODE": E.KEY_F2,
        }

        for action, keycode in expected.items():
            with self.subTest(action=action):
                self.assertEqual(KEY_MAP[action], keycode)

    def test_existing_gameplay_keys_remain_mapped(self):
        expected = {
            "START": E.KEY_1,
            "COIN": E.KEY_5,
            "BET": E.KEY_3,
            "KAN": E.KEY_LEFTCTRL,
            "PON": E.KEY_LEFTALT,
            "CHI": E.KEY_SPACE,
            "REACH": E.KEY_LEFTSHIFT,
            "RON": E.KEY_Z,
            "DOUBLEUP": E.KEY_RIGHTSHIFT,
            "BIG": E.KEY_ENTER,
            "SMALL": E.KEY_BACKSPACE,
        }
        expected.update({
            chr(ord("A") + index): getattr(E, f"KEY_{chr(ord('A') + index)}")
            for index in range(14)
        })

        for action, keycode in expected.items():
            with self.subTest(action=action):
                self.assertEqual(KEY_MAP[action], keycode)


if __name__ == "__main__":
    unittest.main()
