import networkx as nx
import randomneet
import unittest

from neet.boolean.examples import s_pombe
from randomneet.constraints import IsIrreducible, IsConnected, GenericTopological
from randomneet.randomizer import AbstractRandomizer
from randomneet.topology import TopologyRandomizer


class MockTopologyRandomizer(TopologyRandomizer):
    def _randomize(self):
        return nx.DiGraph()


class TestTopologyRandomizers(unittest.TestCase):
    """
    Unit tests for the topology randomizers
    """

    def test_topology_module(self):
        """
        Ensure that TopologyRandomizer is exported from randomneet
        """
        self.assertTrue('topology' in dir(randomneet))

    def test_topology_randomizer(self):
        """
        TopologyRandomizer should be an abstract object
        """
        self.assertTrue(issubclass(TopologyRandomizer, AbstractRandomizer))
        with self.assertRaises(TypeError):
            TopologyRandomizer(s_pombe)  # type: ignore

    def test_topology_randomizer_constraints(self):
        """
        Ensure that the randomizer correctly instantiates the constraints
        """
        c1 = IsConnected()
        rand = MockTopologyRandomizer(s_pombe, constraints=[c1])
        self.assertEqual(rand.network, s_pombe)
        self.assertTrue(nx.is_isomorphic(rand.graph, s_pombe.network_graph()))
        self.assertEqual(rand.timeout, 1000)
        self.assertEqual(rand.constraints, [c1])

        c2 = lambda _: False  # noqa
        rand = MockTopologyRandomizer(s_pombe, constraints=[c2])
        self.assertEqual(rand.network, s_pombe)
        self.assertTrue(nx.is_isomorphic(rand.graph, s_pombe.network_graph()))
        self.assertEqual(rand.timeout, 1000)
        self.assertEqual(len(rand.constraints), 1)
        self.assertIsInstance(rand.constraints[0], GenericTopological)
        self.assertEqual(rand.constraints[0].test, c2)

        with self.assertRaises(TypeError):
            MockTopologyRandomizer(s_pombe, constraints=[IsIrreducible()])

    def test_topology_randomizer_set_constraints(self):
        """
        Ensure that the randomizer correctly instantiates the constraints
        """
        c1 = IsConnected()
        rand = MockTopologyRandomizer(s_pombe)
        rand.constraints = [c1]
        self.assertEqual(rand.constraints, [c1])

        c2 = lambda _: False  # noqa
        rand.constraints = [c2]
        self.assertEqual(len(rand.constraints), 1)
        self.assertIsInstance(rand.constraints[0], GenericTopological)
        self.assertEqual(rand.constraints[0].test, c2)

        rand.constraints = {c1}
        self.assertEqual(rand.constraints, [c1])

        rand.constraints = (c1,)
        self.assertEqual(rand.constraints, [c1])

        with self.assertRaises(TypeError):
            rand.constraints = [IsIrreducible()]

    def test_randomizer_add_constraints(self):
        """
        Ensure that we can add constraints after initialization
        """
        c1, c2 = IsConnected(), (lambda _: False)
        rand = MockTopologyRandomizer(s_pombe)

        rand.add_constraint(c1)
        self.assertEqual(len(rand.constraints), 1)
        self.assertEqual(rand.constraints, [c1])

        rand.add_constraint(c2)
        self.assertEqual(len(rand.constraints), 2)
        self.assertEqual(rand.constraints[0], c1)
        self.assertIsInstance(rand.constraints[1], GenericTopological)
        self.assertEqual(rand.constraints[1].test, c2)

        with self.assertRaises(TypeError):
            rand.add_constraint(IsIrreducible())
