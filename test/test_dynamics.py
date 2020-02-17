import randomneet
import unittest

from neet.boolean.examples import s_pombe
from randomneet.dynamics import NetworkRandomizer
from randomneet.randomizer import AbstractRandomizer
from randomneet.topology import FixedTopology, MeanDegree


class MockNetworkRandomizer(NetworkRandomizer):
    def _randomize(self):
        return self.network


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

    def test_randomizer_trand(self):
        """
        NetworkRandomizer instantiation with TopologyRandomizers
        """
        self.assertIsInstance(MockNetworkRandomizer(s_pombe).trand, FixedTopology)
        self.assertIsInstance(MockNetworkRandomizer(s_pombe, MeanDegree).trand, MeanDegree)
        self.assertIsInstance(MockNetworkRandomizer(s_pombe, MeanDegree(s_pombe)).trand, MeanDegree)
        with self.assertRaises(TypeError):
            MockNetworkRandomizer(s_pombe, AbstractRandomizer)
        with self.assertRaises(TypeError):
            MockNetworkRandomizer(s_pombe, MockNetworkRandomizer(s_pombe))
