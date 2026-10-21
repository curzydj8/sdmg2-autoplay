import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "modules"))

from mahjong_vision import MahjongVision


class MahjongVisionTemplatePathTests(unittest.TestCase):
    def test_default_template_directory_is_project_templates(self):
        vision = MahjongVision()

        self.assertEqual(
            vision.template_dir,
            os.path.join(PROJECT_ROOT, "templates"),
        )
        self.assertTrue(vision.templates)


if __name__ == "__main__":
    unittest.main()
