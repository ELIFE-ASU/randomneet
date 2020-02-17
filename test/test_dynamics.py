import networkx as nx
import randomneet
import unittest

from neet.boolean.examples import s_pombe
from randomneet.dynamics import NetworkRandomizer
from randomneet.constraints import GenericDynamical
from randomneet.randomizer import AbstractRandomizer
from randomneet.topology import FixedTopology, MeanDegree
from randomneet.constraints import IsConnected, IsIrreducible


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

    def test_network_randomizer_trand(self):
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

    def test_network_randomizer_propogates_timeout(self):
        """
        The timeout passed to the NetworkRandomizer initializer is propagated
        to trand when it's a class.
        """
        rand = MockNetworkRandomizer(s_pombe, timeout=5)
        self.assertEqual(rand.timeout, 5)
        self.assertEqual(rand.trand.timeout, 5)

        rand = MockNetworkRandomizer(s_pombe, trand=MeanDegree, timeout=5)
        self.assertEqual(rand.timeout, 5)
        self.assertEqual(rand.trand.timeout, 5)

    def test_network_randomizer_constraints(self):
        """
        Ensure that the randomizer correctly instantiates the constraints
        """
        c1, c2, c3 = IsIrreducible(), (lambda _: False), IsConnected()

        rand = MockNetworkRandomizer(s_pombe, constraints=[c1])
        self.assertEqual(rand.network, s_pombe)
        self.assertTrue(nx.is_isomorphic(rand.graph, s_pombe.network_graph()))
        self.assertEqual(rand.timeout, 1000)
        self.assertEqual(rand.constraints, [c1])
        self.assertEqual(rand.trand.constraints, [])

        rand = MockNetworkRandomizer(s_pombe, constraints=[c2])
        self.assertEqual(rand.network, s_pombe)
        self.assertTrue(nx.is_isomorphic(rand.graph, s_pombe.network_graph()))
        self.assertEqual(rand.timeout, 1000)
        self.assertEqual(len(rand.constraints), 1)
        self.assertIsInstance(rand.constraints[0], GenericDynamical)
        self.assertEqual(rand.constraints[0].test, c2)
        self.assertEqual(rand.trand.constraints, [])

        rand = MockNetworkRandomizer(s_pombe, constraints=[c3])
        self.assertEqual(rand.network, s_pombe)
        self.assertTrue(nx.is_isomorphic(rand.graph, s_pombe.network_graph()))
        self.assertEqual(rand.timeout, 1000)
        self.assertEqual(rand.constraints, [])
        self.assertEqual(rand.trand.constraints, [c3])

        rand = MockNetworkRandomizer(s_pombe, constraints=[c1, c3, c2])
        self.assertEqual(rand.network, s_pombe)
        self.assertTrue(nx.is_isomorphic(rand.graph, s_pombe.network_graph()))
        self.assertEqual(rand.timeout, 1000)
        self.assertEqual(len(rand.constraints), 2)
        self.assertEqual(rand.constraints[0], c1)
        self.assertIsInstance(rand.constraints[1], GenericDynamical)
        self.assertEqual(rand.constraints[1].test, c2)
        self.assertEqual(rand.trand.constraints, [c3])

        with self.assertRaises(TypeError):
            MockNetworkRandomizer(s_pombe, constraints=[5])

    def test_network_randomizer_set_constraints(self):
        """
        Ensure that the randomizer correctly sets the constraints
        """
        c1, c2, c3 = IsIrreducible(), (lambda _: False), IsConnected()

        rand = MockNetworkRandomizer(s_pombe)

        rand.constraints = [c1]
        self.assertEqual(rand.constraints, [c1])
        self.assertEqual(rand.trand.constraints, [])

        rand.constraints = [c2]
        self.assertEqual(len(rand.constraints), 1)
        self.assertIsInstance(rand.constraints[0], GenericDynamical)
        self.assertEqual(rand.constraints[0].test, c2)
        self.assertEqual(rand.trand.constraints, [])

        rand.constraints = [c3]
        self.assertEqual(rand.constraints, [])
        self.assertEqual(rand.trand.constraints, [c3])

        rand.constraints = [c1, c2, c3]
        self.assertEqual(len(rand.constraints), 2)
        self.assertEqual(rand.constraints[0], c1)
        self.assertIsInstance(rand.constraints[1], GenericDynamical)
        self.assertEqual(rand.constraints[1].test, c2)
        self.assertEqual(rand.trand.constraints, [c3])

        rand.constraints = {c1}
        self.assertEqual(rand.constraints, [c1])
        self.assertEqual(rand.trand.constraints, [])

        rand.constraints = (c3,)
        self.assertEqual(rand.constraints, [])
        self.assertEqual(rand.trand.constraints, [c3])

        with self.assertRaises(TypeError):
            rand.constraints = [5]
