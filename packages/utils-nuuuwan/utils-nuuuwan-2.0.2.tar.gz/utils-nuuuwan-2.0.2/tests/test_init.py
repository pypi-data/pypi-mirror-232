import unittest

from utils import WWW, Color, Git, Tweet


class TestCase(unittest.TestCase):
    def test_init(self):
        self.assertIsNotNone(Color)
        self.assertIsNotNone(Git)
        self.assertIsNotNone(Tweet)
        self.assertIsNotNone(WWW)
