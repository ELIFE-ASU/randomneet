import randomneet
import randomneet.constraints
import unittest


class TestConstraints(unittest.TestCase):
    """
    Unit tests for the various network constraints.
    """

    def test_constraints_module(self):
        """
        Ensure that constraints is exported from randomneet
        """
        self.assertTrue('constraints' in dir(randomneet))
