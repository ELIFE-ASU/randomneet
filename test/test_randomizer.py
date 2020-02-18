import networkx as nx
import randomneet
import unittest

from neet.boolean.examples import s_pombe, myeloid
from randomneet.randomizer import AbstractRandomizer
from randomneet.constraints import IsIrreducible, IsConnected, GenericTopological, ConstraintError
from itertools import islice


class MockRandomizer(AbstractRandomizer):
    """
    A mock implementation of the AbstractRandomizer base class
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0

    def _randomize(self):
        """
        Generate successively larger empty graphs
        """
        g = nx.DiGraph()
        g.add_nodes_from(range(self.counter))
        self.counter += 1
        return g


class TestRandomizer(unittest.TestCase):
    """
    Unit tests for the abstract randomizer and it's ilk
    """

    def test_randomizer_module(self):
        """
        Ensure that randomizer is exported from randomneet
        """
        self.assertTrue('randomizer' in dir(randomneet))

    def test_abstract_randomizer(self):
        """
        The AbstractRandomizer should be an abstract object
        """
        self.assertTrue(issubclass(AbstractRandomizer, object))
        with self.assertRaises(TypeError):
            AbstractRandomizer()  # type: ignore

    def test_randomizer_default_init(self):
        """
        Ensure that randomizer correctly initializes with default arguments
        """
        g = nx.DiGraph([(0, 1), (1, 1)])
        rand = MockRandomizer(g)
        self.assertIsNone(rand.network)
        self.assertEqual(rand.graph, g)
        self.assertEqual(rand.timeout, 1000)
        self.assertEqual(rand.constraints, [])

        rand = MockRandomizer(s_pombe)
        self.assertEqual(rand.network, s_pombe)
        self.assertTrue(nx.is_isomorphic(rand.graph, s_pombe.network_graph()))
        self.assertEqual(rand.timeout, 1000)
        self.assertEqual(rand.constraints, [])

        with self.assertRaises(TypeError):
            MockRandomizer(None)

        with self.assertRaises(TypeError):
            MockRandomizer(nx.Graph())

    def test_randomizer_init_constraints(self):
        """
        Ensure that the randomizer correctly instantiates the constraints
        """
        constraint = IsIrreducible()
        rand = MockRandomizer(s_pombe, constraints=[constraint])
        self.assertEqual(rand.network, s_pombe)
        self.assertTrue(nx.is_isomorphic(rand.graph, s_pombe.network_graph()))
        self.assertEqual(rand.timeout, 1000)
        self.assertEqual(rand.constraints, [constraint])

        with self.assertRaises(TypeError):
            MockRandomizer(s_pombe, constraints=[lambda n: False])

    def test_randomizer_init_timeout(self):
        """
        Ensure that the randomizer correctly sets the timeout
        """
        rand = MockRandomizer(s_pombe, timeout=0)
        self.assertEqual(rand.network, s_pombe)
        self.assertTrue(nx.is_isomorphic(rand.graph, s_pombe.network_graph()))
        self.assertEqual(rand.timeout, 0)
        self.assertEqual(rand.constraints, [])

    def test_randomizer_set_network(self):
        """
        Ensure that we can set the network after initialization
        """
        rand = MockRandomizer(s_pombe)
        rand.network = myeloid
        self.assertEqual(rand.network, myeloid)
        self.assertTrue(nx.is_isomorphic(rand.graph, myeloid.network_graph()))

        with self.assertRaises(TypeError):
            rand.network = nx.DiGraph()

    def test_randomizer_set_graph(self):
        """
        Ensure that we can set the graph after initialization
        """
        rand = MockRandomizer(s_pombe)
        rand.graph = nx.DiGraph([(0, 1), (1, 1)])
        self.assertIsNone(rand.network)
        self.assertTrue(nx.is_isomorphic(rand.graph, nx.DiGraph([(0, 1), (1, 1)])))

        with self.assertRaises(TypeError):
            rand.graph = s_pombe

    def test_randomizer_set_constraints(self):
        """
        Ensure that we can set the constraints after initialization
        """
        constraint = IsIrreducible()
        rand = MockRandomizer(s_pombe, constraints=[IsConnected()])
        rand.constraints = [constraint]
        self.assertEqual(rand.constraints, [constraint])

        rand.constraints = {constraint}
        self.assertEqual(rand.constraints, [constraint])

        rand.constraints = (constraint,)
        self.assertEqual(rand.constraints, [constraint])

        with self.assertRaises(TypeError):
            rand.constraints = [lambda _: True]

    def test_randomizer_add_constraints(self):
        """
        Ensure that we can add constraints after initialization
        """
        c1, c2 = IsIrreducible(), IsConnected()
        rand = MockRandomizer(s_pombe, constraints=[c1])
        rand.add_constraint(c2)
        self.assertEqual(rand.constraints, [c1, c2])

        with self.assertRaises(TypeError):
            rand.add_constraint(lambda _: True)

    def test_randomizer_random_with_timeout(self):
        """
        Ensure that random times out properly
        """
        constraint = GenericTopological(lambda _: False)
        rand = MockRandomizer(s_pombe, constraints=[constraint], timeout=10)
        with self.assertRaises(ConstraintError):
            rand.random()

    def test_randomizer_random(self):
        """
        Ensure that random can generate something
        """
        constraint = GenericTopological(lambda g: len(g) == 3)
        rand = MockRandomizer(s_pombe, constraints=[constraint])
        g = rand.random()
        self.assertEqual(len(g), 3)

    def test_randomizers_are_iterable(self):
        """
        Ensure that randomizers are iterable.
        """
        def take(n, iter):
            return islice(iter, n)

        rand = MockRandomizer(s_pombe)
        gs = list(map(len, take(5, rand)))
        self.assertEqual(gs, [0, 1, 2, 3, 4])
