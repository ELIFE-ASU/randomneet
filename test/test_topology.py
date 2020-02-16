import networkx as nx
import randomneet
import unittest

from collections import Counter
from itertools import islice
from neet.boolean.examples import s_pombe
from randomneet.constraints import IsIrreducible, IsConnected, GenericTopological, ConstraintError
from randomneet.randomizer import AbstractRandomizer
from randomneet.topology import TopologyRandomizer, FixedTopology, MeanDegree, InDegree, OutDegree


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

    def test_topology_randomizer_add_constraints(self):
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

    def test_fixed_topology_constraints(self):
        """
        Ensure that the randomizer correctly instantiates the constraints
        """
        c1 = IsConnected()
        rand = FixedTopology(s_pombe, constraints=[c1])
        self.assertEqual(rand.network, s_pombe)
        self.assertTrue(nx.is_isomorphic(rand.graph, s_pombe.network_graph()))
        self.assertEqual(rand.timeout, 1000)
        self.assertEqual(rand.constraints, [c1])

        c2 = lambda _: True  # noqa
        rand = FixedTopology(s_pombe, constraints=[c2])
        self.assertEqual(rand.network, s_pombe)
        self.assertTrue(nx.is_isomorphic(rand.graph, s_pombe.network_graph()))
        self.assertEqual(rand.timeout, 1000)
        self.assertEqual(len(rand.constraints), 1)
        self.assertIsInstance(rand.constraints[0], GenericTopological)
        self.assertEqual(rand.constraints[0].test, c2)

        with self.assertRaises(ConstraintError):
            FixedTopology(s_pombe, constraints=[lambda _: False])

        with self.assertRaises(TypeError):
            FixedTopology(s_pombe, constraints=[IsIrreducible()])

    def test_fixed_topology_set_constraints(self):
        """
        Ensure that the randomizer correctly instantiates the constraints
        """
        c1 = IsConnected()
        rand = FixedTopology(s_pombe)
        rand.constraints = [c1]
        self.assertEqual(rand.constraints, [c1])

        c2 = lambda _: True  # noqa
        rand.constraints = [c2]
        self.assertEqual(len(rand.constraints), 1)
        self.assertIsInstance(rand.constraints[0], GenericTopological)
        self.assertEqual(rand.constraints[0].test, c2)

        rand.constraints = {c1}
        self.assertEqual(rand.constraints, [c1])

        rand.constraints = (c1,)
        self.assertEqual(rand.constraints, [c1])

        with self.assertRaises(ConstraintError):
            rand.constraints = [lambda _: False]

        with self.assertRaises(TypeError):
            rand.constraints = [IsIrreducible()]

    def test_fixed_topology_add_constraints(self):
        """
        Ensure that we can add constraints after initialization
        """
        c1, c2 = IsConnected(), (lambda _: True)
        rand = FixedTopology(s_pombe)

        rand.add_constraint(c1)
        self.assertEqual(len(rand.constraints), 1)
        self.assertEqual(rand.constraints, [c1])

        rand.add_constraint(c2)
        self.assertEqual(len(rand.constraints), 2)
        self.assertEqual(rand.constraints[0], c1)
        self.assertIsInstance(rand.constraints[1], GenericTopological)
        self.assertEqual(rand.constraints[1].test, c2)

        with self.assertRaises(ConstraintError):
            rand.add_constraint(lambda _: False)

        with self.assertRaises(TypeError):
            rand.add_constraint(IsIrreducible())

    def test_fixed_topology(self):
        """
        Ensure that the topologies generated are isomorphic to the original topology
        """
        g = nx.DiGraph([(0, 1), (1, 1), (2, 1)])
        rand = FixedTopology(g)
        self.assertTrue(all(map(lambda h: nx.is_isomorphic(g, h), islice(rand, 10))))

        g = s_pombe.network_graph()
        rand = FixedTopology(g)
        self.assertTrue(all(map(lambda h: nx.is_isomorphic(g, h), islice(rand, 10))))

    def test_fixed_mean_degree(self):
        """
        Ensure that the topologies generated by MeanDegree have the same number
        of nodes and edges, and the same degree distribution as the original
        topology
        """
        def mean_degree(g):
            return sum(dict(g.degree).values()) / len(g)

        g = nx.DiGraph([(0, 1), (1, 1), (2, 1)])
        rand = MeanDegree(g)
        for h in islice(rand, 100):
            self.assertTrue(len(h), len(g))
            self.assertTrue(h.size, g.size)
            try:
                self.assertEqual(mean_degree(h), mean_degree(g))
            except Exception as err:
                raise Exception(h.degree, g.degree) from err

        g = s_pombe.network_graph()
        rand = MeanDegree(g)
        for h in islice(rand, 100):
            self.assertTrue(len(h), len(g))
            self.assertTrue(h.size, g.size)
            try:
                self.assertEqual(mean_degree(h), mean_degree(g))
            except Exception as err:
                raise Exception(h.degree, g.degree) from err

    def test_fixed_in_degree(self):
        """
        Ensure that the topologies generated by InDegree have the same number
        of nodes and edges, and the same in-degree distribution as the original
        topology
        """
        def in_degree(g):
            return Counter(dict(g.in_degree).values())

        g = nx.DiGraph([(0, 1), (1, 1), (2, 1)])
        rand = InDegree(g)
        for h in islice(rand, 100):
            self.assertTrue(len(h), len(g))
            self.assertTrue(h.size, g.size)
            try:
                self.assertEqual(in_degree(h), in_degree(g))
            except Exception as err:
                raise Exception(h.in_degree, g.in_degree) from err

        g = s_pombe.network_graph()
        rand = InDegree(g)
        for h in islice(rand, 100):
            self.assertTrue(len(h), len(g))
            self.assertTrue(h.size, g.size)
            try:
                self.assertEqual(in_degree(h), in_degree(g))
            except Exception as err:
                raise Exception(h.in_degree, g.in_degree) from err

    def test_fixed_out_degree(self):
        """
        Ensure that the topologies generated by OutDegree have the same number
        of nodes and edges, and the same out-degree distribution as the
        original topology
        """
        def out_degree(g):
            return Counter(dict(g.out_degree).values())

        g = nx.DiGraph([(0, 1), (1, 1), (2, 1)])
        rand = OutDegree(g)
        for h in islice(rand, 100):
            self.assertTrue(len(h), len(g))
            self.assertTrue(h.size, g.size)
            try:
                self.assertEqual(out_degree(h), out_degree(g))
            except Exception as err:
                raise Exception(h.in_degree, g.in_degree) from err

        g = s_pombe.network_graph()
        rand = OutDegree(g)
        for h in islice(rand, 100):
            self.assertTrue(len(h), len(g))
            self.assertTrue(h.size, g.size)
            try:
                self.assertEqual(out_degree(h), out_degree(g))
            except Exception as err:
                raise Exception(h.in_degree, g.in_degree) from err
