import randomneet  # noqa
import unittest


class TestCoalMine(unittest.TestCase):
    """
    Canary test to make sure the test suite is working.
    """

    def test_air(self):
        """
        The bird dies if this test doesn't run or fails.
        """
        self.assertEqual(1 + 2, 3)
