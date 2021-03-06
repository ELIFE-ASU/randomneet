import math
import networkx as nx
import randomneet
import statistics
import unittest

from neet.boolean.examples import s_pombe, myeloid
from randomneet.dynamics import NetworkRandomizer, UniformBias, MeanBias, LocalBias, \
    FixCanalizingMixin
from randomneet.constraints import GenericDynamical, GenericTopological, ConstraintError
from randomneet.randomizer import AbstractRandomizer
from randomneet.topology import TopologyRandomizer, FixedTopology, MeanDegree, InDegree
from randomneet.constraints import IsConnected, IsIrreducible
from itertools import islice


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


class TestUniformBias(unittest.TestCase):
    """
    Unit tests for the UniformBias randomizer
    """

    def bias(self, network):
        """
        Get the bias of each node in the network
        """
        return [float(len(row[1]) / 2**len(row[0])) for row in network.table]

    def test_uniform_bias(self):
        """
        Ensure that UniformBias is a NetworkRandomizer
        """
        self.assertIsInstance(UniformBias(myeloid), NetworkRandomizer)

    def test_default_bias(self):
        """
        Ensure the generated networks have a bias of 0.5 by default
        """
        rand = UniformBias(s_pombe)
        s_pombe_graph = s_pombe.network_graph()
        indegree = [s_pombe_graph.in_degree(n) for n in sorted(s_pombe_graph.nodes)]
        expect = [0.0 if s_pombe_graph.in_degree(n) == 0 else 0.5 for n in indegree]
        got = list(map(self.bias, islice(rand, 10)))
        self.assertEqual(got, [expect] * len(got))

    def test_other_bias(self):
        """
        Ensure the generated networks have the specified
        """
        p = 0.3

        rand = UniformBias(s_pombe, p)
        s_pombe_graph = s_pombe.network_graph()
        indegree = [s_pombe_graph.in_degree(n) for n in sorted(s_pombe_graph.nodes)]
        high = [0.0 if k == 0 else math.ceil(p * 2**k) / 2**k for k in indegree]
        low = [0.0 if k == 0 else math.floor(p * 2**k) / 2**k for k in indegree]
        for net in islice(rand, 10):
            got = self.bias(net)
            for g, l, h in zip(got, low, high):
                self.assertTrue(g == l or g == h)


class TestMeanBias(unittest.TestCase):
    """
    Unit tests for the MeanBias randomizer
    """

    def test_mean_bias(self):
        """
        Ensure that MeanBias is a UniformBias
        """
        self.assertIsInstance(MeanBias(myeloid), UniformBias)

    def test_unimplemented(self):
        """
        MeanBias is currently only implemented for logic network
        """
        with self.assertRaises(NotImplementedError):
            MeanBias(s_pombe)

    def test_bias(self):
        """
        Ensure the generated networks have a the same mean bias as the original
        network (on average).
        """
        rand = MeanBias(myeloid)
        got = statistics.mean(map(rand._mean_bias, islice(rand, 100)))
        self.assertAlmostEqual(got, rand.p, delta=0.01)


class TestLocalBias(unittest.TestCase):
    """
    Unit tests for the LocalBias randomizer
    """

    def test_local_bias(self):
        """
        Ensure that LocalBias is a NetworkRandomizer
        """
        self.assertIsInstance(LocalBias(myeloid), NetworkRandomizer)

    def test_unimplemented(self):
        """
        LocalBias is currently only implemented for logic networks with
        FixedTopology or FixedInDegree topological randomizers
        """
        with self.assertRaises(NotImplementedError):
            LocalBias(s_pombe)

        with self.assertRaises(NotImplementedError):
            LocalBias(myeloid, MeanDegree)

        with self.assertRaises(NotImplementedError):
            LocalBias(myeloid, MeanDegree(myeloid))

    def test_bias(self):
        def local_bias(network):
            return [len(row[1]) / 2**len(row[0]) for row in network.table]

        rand = LocalBias(myeloid)
        myeloid_graph = myeloid.network_graph()
        myeloid_indegree = [myeloid_graph.in_degree(n) for n in sorted(myeloid_graph.nodes)]
        expected_bias = local_bias(myeloid)
        for net in islice(rand, 1):
            self.assertTrue(nx.is_isomorphic(net.network_graph(), myeloid_graph))
            self.assertEqual(local_bias(net), expected_bias)

        rand = LocalBias(myeloid, InDegree)
        for net in islice(rand, 100):
            graph = net.network_graph()
            indegree = [graph.in_degree(n) for n in sorted(graph.nodes)]
            self.assertEqual(indegree, myeloid_indegree)
            self.assertEqual(local_bias(net), expected_bias)


class CanalizingUniformBias(FixCanalizingMixin, UniformBias):
    pass


class TestCanalizingMixin(unittest.TestCase):
    def test_canalizing(self):
        expected = s_pombe.canalizing_nodes()

        rand = UniformBias(s_pombe)
        failures = sum(map(lambda n: not expected.issubset(n.canalizing_nodes()),
                           islice(rand, 100)))
        self.assertGreater(failures, 0)

        rand = CanalizingUniformBias(s_pombe)
        failures = sum(map(lambda n: expected.issubset(n.canalizing_nodes()), islice(rand, 100)))
        failures = sum(map(lambda n: not expected.issubset(n.canalizing_nodes()),
                           islice(rand, 100)))
        self.assertEqual(failures, 0)

        rand = CanalizingUniformBias(s_pombe, 0.25)
        failures = sum(map(lambda n: expected.issubset(n.canalizing_nodes()), islice(rand, 100)))
        failures = sum(map(lambda n: not expected.issubset(n.canalizing_nodes()),
                           islice(rand, 100)))
        self.assertEqual(failures, 0)

        rand = CanalizingUniformBias(s_pombe, 0.75)
        failures = sum(map(lambda n: expected.issubset(n.canalizing_nodes()), islice(rand, 100)))
        failures = sum(map(lambda n: not expected.issubset(n.canalizing_nodes()),
                           islice(rand, 100)))
        self.assertEqual(failures, 0)

        rand = CanalizingUniformBias(nx.complete_graph(9, nx.DiGraph))
        with self.assertRaises(NotImplementedError):
            rand.random()
