import randomneet
import unittest

from neet.boolean.examples import s_pombe
from randomneet.dynamics import NetworkRandomizer
from randomneet.randomizer import AbstractRandomizer


class TestDynamicsRandomizer(unittest.TestCase):
    """
    Unit tests for the dynamics randomizers
    """

    def test_dynamics_module(self):
        """
        Ensure that DynamicsRandomizer is exported from randomneet
        """
        self.assertTrue('dynamics' in dir(randomneet))

    def test_network_randomizer(self):
        """
        NetworkRandomizer should be an abstract object
        """
        self.assertTrue(issubclass(NetworkRandomizer, AbstractRandomizer))
        with self.assertRaises(TypeError):
            NetworkRandomizer(s_pombe)  # type: ignore
