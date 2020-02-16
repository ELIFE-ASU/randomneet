import randomneet
import unittest


class TestRandomizer(unittest.TestCase):
    """
    Unit tests for the abstract randomizer and it's ilk
    """

    def test_randomizer_module(self):
        """
        Ensure that randomizer is exported from randomneet
        """
        self.assertTrue('randomizer' in dir(randomneet))
