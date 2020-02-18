import networkx as nx
import randomneet
import unittest

from neet.boolean.examples import s_pombe
from randomneet.dynamics import NetworkRandomizer
from randomneet.constraints import GenericDynamical, GenericTopological, ConstraintError
from randomneet.randomizer import AbstractRandomizer
from randomneet.topology import TopologyRandomizer, FixedTopology, MeanDegree
from randomneet.constraints import IsConnected, IsIrreducible


class MockTopologyRandomizer(TopologyRandomizer):
    """
    A mock implementation of the AbstractRandomizer base class
    """
    counter = 0

    def _randomize(self):
        """
        Generate successively larger empty graphs
        """
        self.counter += 1
        return nx.DiGraph([(i, j) for i in range(self.counter) for j in range(self.counter)])


class MockNetworkRandomizer(NetworkRandomizer):
    p = 0.0

    def _randomize(self, topology):
        network = super()._randomize(topology)
        self.p += 0.1
        return network

    def _function_class_parameters(self, topology, node):
        """
        Generate parameters with successively higher bias
        """
        d = super()._function_class_parameters(topology, node)
        d.update({'k': topology.in_degree(node), 'p': self.p})
        return d


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

    def test_network_randomizer_add_constraints(self):
        """
        Ensure that the randomizer correctly adds the constraints
        """
        c1, c2, c3 = IsIrreducible(), (lambda _: False), IsConnected()

        rand = MockNetworkRandomizer(s_pombe)

        rand.add_constraint(c1)
        self.assertEqual(rand.constraints, [c1])
        self.assertEqual(rand.trand.constraints, [])

        rand.add_constraint(c2)
        self.assertEqual(len(rand.constraints), 2)
        self.assertEqual(rand.constraints[0], c1)
        self.assertIsInstance(rand.constraints[1], GenericDynamical)
        self.assertEqual(rand.constraints[1].test, c2)
        self.assertEqual(rand.trand.constraints, [])

        rand.add_constraint(c3)
        self.assertEqual(len(rand.constraints), 2)
        self.assertEqual(rand.constraints[0], c1)
        self.assertIsInstance(rand.constraints[1], GenericDynamical)
        self.assertEqual(rand.constraints[1].test, c2)
        self.assertEqual(rand.trand.constraints, [c3])

        with self.assertRaises(TypeError):
            rand.add_constraint(5)

    def test_random_timeout(self):
        """
        Ensure the randomizer times out properly
        """
        def allfail(_):
            return False

        tc, dc = GenericTopological(allfail), GenericDynamical(allfail)
        rand = MockNetworkRandomizer(s_pombe, MockTopologyRandomizer, constraints=[tc], timeout=10)
        with self.assertRaises(ConstraintError):
            rand.random()

        rand = MockNetworkRandomizer(s_pombe, MockTopologyRandomizer, constraints=[dc], timeout=10)
        with self.assertRaises(ConstraintError):
            rand.random()

    def test_random(self):
        def bias(network):
            return [float(len(row[1]) / 2**len(row[0])) for row in network.table]

        rand = MockNetworkRandomizer(s_pombe, MockTopologyRandomizer, timeout=20)
        rand.add_constraint(lambda n: bias(n) == [1.0] * n.size)
        rand.add_constraint(GenericTopological(lambda g: len(g) == 10))

        network = rand.random()
        self.assertEqual(len(network.network_graph()), 10)
