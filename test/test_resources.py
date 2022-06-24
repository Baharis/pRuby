import unittest
from pruby.resources import icon


class TestIcon(unittest.TestCase):
    def test_icon_exists(self):
        self.assertIsInstance(icon, bytes)


if __name__ == '__main__':
    unittest.main()
