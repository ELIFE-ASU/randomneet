import randomneet
import unittest

from randomneet.dynamics import NetworkRandomizer
from randomneet.randomizer import AbstractRandomizer


class TestNetworkRandomizer(unittest.TestCase):
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
