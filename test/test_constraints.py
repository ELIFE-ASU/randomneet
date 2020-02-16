import networkx as nx
import randomneet
import unittest

from neet.boolean import LogicNetwork
from neet.boolean.examples import s_pombe, myeloid
from randomneet.constraints import AbstractConstraint, TopologicalConstraint, DynamicalConstraint, \
    HasExternalNodes, IsConnected, IsIrreducible, \
    HasCanalizingNodes, GenericTopological, GenericDynamical, \
    ConstraintError


class TestConstraints(unittest.TestCase):
    """
    Unit tests for the various network constraints.
    """

    def empty_graph(self, n=0):
        """
        Create a directed graph with no edges and ``n`` nodes.
        """
        g = nx.DiGraph()
        g.add_nodes_from(range(n))
        return g

    def test_constraints_module(self):
        """
        Ensure that constraints is exported from randomneet
        """
        self.assertTrue('constraints' in dir(randomneet))

    def test_abstract_constraint(self):
        """
        The AbstractConstraint should be an abstract object
        """
        self.assertTrue(issubclass(AbstractConstraint, object))
        with self.assertRaises(TypeError):
            AbstractConstraint()  # type: ignore

    def test_topological_constraint(self):
        """
        The TopologicalConstraint should be an abstract subclass of
        AbstractConstraint
        """
        self.assertTrue(issubclass(TopologicalConstraint, AbstractConstraint))
        with self.assertRaises(TypeError):
            TopologicalConstraint()  # type: ignore

    def test_dynamical_constraint(self):
        """
        The DynamicalConstraint should be an abstract subclass of
        AbstractConstraint
        """
        self.assertTrue(issubclass(DynamicalConstraint, AbstractConstraint))
        with self.assertRaises(TypeError):
            DynamicalConstraint()  # type: ignore

    def test_has_external_nodes_is_topological(self):
        """
        The HasExternalNodes constraint is a TopologicalConstraint
        """
        self.assertTrue(issubclass(HasExternalNodes, TopologicalConstraint))

    def test_has_external_nodes_invalid_init(self):
        """
        HasExternalNodes should raise a Value or TypeError for invalid
        initialization parameters.
        """
        with self.assertRaises(ValueError):
            HasExternalNodes(-1)
        with self.assertRaises(TypeError):
            HasExternalNodes(nx.Graph())

    def test_has_external_nodes_counts(self):
        """
        HasExternalNodes properly counts the number of external nodes in a
        directed graph.
        """
        g = nx.DiGraph([(0, 1), (1, 2), (2, 1), (3, 1), (4, 5), (6, 6)])
        constraint = HasExternalNodes(g)
        self.assertEqual(constraint.num_external, 3)

    def test_has_external_nodes_saves_target(self):
        """
        HasExternalNodes properly stores the desired number of external edges.
        """
        self.assertEqual(HasExternalNodes(7).num_external, 7)

    def test_has_external_nodes_raises(self):
        """
        HasExternalNodes.satisfies raises an error if the provided argument is
        not a directed graph.
        """
        constraint = HasExternalNodes(3)
        with self.assertRaises(TypeError):
            constraint.satisfies(3)
        with self.assertRaises(TypeError):
            constraint.satisfies(nx.Graph())

    def test_has_external_nodes_satisfies(self):
        """
        HasExternalNodes.satsifies correctly identifies directed graphs with
        the desired number of external nodes.
        """
        g = nx.DiGraph([(0, 1), (1, 2), (2, 1), (3, 1), (4, 5), (6, 6)])

        constraint = HasExternalNodes(3)
        self.assertFalse(constraint.satisfies(nx.DiGraph()))
        self.assertFalse(constraint.satisfies(nx.DiGraph([(0, 1), (1, 2), (2, 1), (3, 2)])))
        self.assertTrue(constraint.satisfies(g))

        constraint = HasExternalNodes(g)
        self.assertFalse(constraint.satisfies(nx.DiGraph()))
        self.assertFalse(constraint.satisfies(nx.DiGraph([(0, 1), (1, 2), (2, 1), (3, 2)])))
        self.assertTrue(constraint.satisfies(g))
        self.assertTrue(constraint.satisfies(nx.DiGraph([(1, 2), (3, 4), (5, 6), (7, 7)])))

    def test_is_connected_is_topological(self):
        """
        The IsConnected constraint is a TopologicalConstraint
        """
        self.assertTrue(issubclass(IsConnected, TopologicalConstraint))

    def test_is_connected_raises(self):
        """
        IsConnected.satisfies raises an error if the provided argument is not a
        directed graph.
        """
        constraint = HasExternalNodes(3)
        with self.assertRaises(TypeError):
            constraint.satisfies(3)
        with self.assertRaises(TypeError):
            constraint.satisfies(nx.Graph())

    def test_is_connected_null_graph(self):
        """
        IsConnected.satisfies raises an error if the provided argument is the
        null graph.
        """
        constraint = IsConnected()
        with self.assertRaises(ConstraintError):
            constraint.satisfies(nx.DiGraph())

    def test_is_connected_satisfies(self):
        """
        IsConnected.satisfies correctly identifies directed graphs that are
        weakly connected.
        """
        constraint = IsConnected()
        self.assertTrue(constraint.satisfies(self.empty_graph(1)))
        self.assertTrue(constraint.satisfies(nx.DiGraph([(0, 0)])))
        self.assertFalse(constraint.satisfies(self.empty_graph(2)))
        self.assertFalse(constraint.satisfies(nx.DiGraph([(0, 0), (1, 1)])))
        self.assertTrue(constraint.satisfies(nx.DiGraph([(0, 1)])))

    @unittest.skip("Tracking down hanging test on Windows")
    def test_is_irreducibile_is_dynamical(self):
        """
        The IsIrreducible constraint is a DynamicalConstraint.
        """
        self.assertTrue(issubclass(IsIrreducible, DynamicalConstraint))

    @unittest.skip("Tracking down hanging test on Windows")
    def test_is_irreducible_raises(self):
        """
        IsIrreducible.satisfies raises an error if the argument is not a Neet
        network.
        """
        constraint = IsIrreducible()
        with self.assertRaises(TypeError):
            constraint.satisfies(nx.DiGraph())
        with self.assertRaises(TypeError):
            constraint.satisfies(nx.Graph())

    @unittest.skip("Tracking down hanging test on Windows")
    def test_is_irreducible_satisfies_non_logic(self):
        """
        IsIrreducible.satisfies is not implemented for non-LogicNetworks
        """
        constraint = IsIrreducible()
        with self.assertRaises(NotImplementedError):
            constraint.satisfies(s_pombe)

    @unittest.skip("Tracking down hanging test on Windows")
    def test_is_irreducible_satisfies(self):
        """
        IsIrreducible.satisfies correctly identifies networks that are
        irreducible.
        """
        constraint = IsIrreducible()
        self.assertTrue(constraint.satisfies(myeloid))

        reducible = LogicNetwork([((0,), {'0', '1'})])
        self.assertFalse(constraint.satisfies(reducible))

        reducible = LogicNetwork([((0, 1), {'01', '11'}),
                                  ((0, 1), {'00', '01', '11'})])
        self.assertFalse(constraint.satisfies(reducible))

        reducible = LogicNetwork([((1,), {'0'}),
                                  ((0, 1), {'01', '11'})])
        self.assertFalse(constraint.satisfies(reducible))

        irreducible = LogicNetwork([((0,), {'0'})])
        self.assertTrue(constraint.satisfies(irreducible))

        irreducible = LogicNetwork([((0, 1), {'01'}),
                                    ((0, 1), {'00', '01', '11'})])
        self.assertTrue(constraint.satisfies(irreducible))

        irreducible = LogicNetwork([((1,), {'0'}),
                                    ((0, 1), {'01', '11', '10'})])
        self.assertTrue(constraint.satisfies(irreducible))

    def test_has_canalizing_nodes_is_dynamical(self):
        """
        The HasCanalizingNodes constraint is a DynamicalConstraint
        """
        self.assertTrue(issubclass(HasCanalizingNodes, DynamicalConstraint))

    def test_has_canalizing_nodes_invalid_init(self):
        """
        HasCanalizingNodes should raise a ValueError or TypeError for invalid
        initialization parameters.
        """
        with self.assertRaises(ValueError):
            HasCanalizingNodes(-1)
        with self.assertRaises(TypeError):
            HasCanalizingNodes(nx.Graph())

    def test_has_canalizing_nodes_counts(self):
        """
        HasCanalizingNodes properly counts the number of canalizing nodes in a
        network.
        """
        constraint = HasCanalizingNodes(myeloid)
        self.assertEqual(constraint.num_canalizing, 11)

        constraint = HasCanalizingNodes(s_pombe)
        self.assertEqual(constraint.num_canalizing, 5)

    def test_has_canalizing_nodes_saves_target(self):
        """
        HasCanalizingNodes properly stores the desired number of external
        edges.
        """
        self.assertEqual(HasCanalizingNodes(7).num_canalizing, 7)

    def test_has_canalizing_nodes_raises(self):
        """
        HasCanalizingNodes.satisfies raises an error if the provided argument
        is not a neet network
        """
        constraint = HasCanalizingNodes(3)
        with self.assertRaises(TypeError):
            constraint.satisfies(3)
        with self.assertRaises(TypeError):
            constraint.satisfies(nx.Graph())
        with self.assertRaises(TypeError):
            constraint.satisfies(nx.DiGraph())

    def test_has_canalizing_nodes_satisfies(self):
        """
        HasCanalizingNodes.satsifies correctly identifies networks the desired
        number of canalizing nodes.
        """
        constraint = HasCanalizingNodes(myeloid)
        self.assertTrue(constraint.satisfies(myeloid))
        self.assertFalse(constraint.satisfies(s_pombe))

    def test_generic_topological_is_topological(self):
        """
        Ensure that GenericTopological is a subclass of TopologicalConstraint.
        """
        self.assertTrue(issubclass(GenericTopological, TopologicalConstraint))

    def test_generic_topological_raises(self):
        """
        GenericTopological raises a TypeError if it's instantiated with
        anything that is not callable.
        """
        with self.assertRaises(TypeError):
            GenericTopological(5)
        with self.assertRaises(TypeError):
            GenericTopological(IsConnected())

    def test_generic_topological_satisfies_raises(self):
        """
        GenericTopological.satisfies raises a TypeError when its argument is
        not a directed graph.
        """
        allpass = GenericTopological(lambda g: True)
        with self.assertRaises(TypeError):
            allpass.satisfies(nx.Graph())
        with self.assertRaises(TypeError):
            allpass.satisfies(s_pombe)

    def test_generic_topological_satisfies(self):
        """
        GenericTopological.satisfies correctly checks graphs.
        """
        allpass = GenericTopological(lambda g: True)
        self.assertTrue(allpass.satisfies(self.empty_graph()))
        self.assertTrue(allpass.satisfies(nx.DiGraph([(0, 1), (1, 2), (2, 0)])))

        allfail = GenericTopological(lambda g: False)
        self.assertFalse(allfail.satisfies(self.empty_graph()))
        self.assertFalse(allfail.satisfies(nx.DiGraph([(0, 1), (1, 2), (2, 0)])))

        twonodes = GenericTopological(lambda g: len(g) == 2)
        self.assertFalse(twonodes.satisfies(self.empty_graph()))
        self.assertTrue(twonodes.satisfies(self.empty_graph(2)))

    def test_generic_dynamical_is_dynamical(self):
        """
        Ensure that GenericDynamical is a subclass of DynamicalConstraint.
        """
        self.assertTrue(issubclass(GenericDynamical, DynamicalConstraint))

    def test_generic_dynamical_raises(self):
        """
        GenericDynamical raises a TypeError if it's instantiated with anything
        that is not callable.
        """
        with self.assertRaises(TypeError):
            GenericDynamical(5)
        with self.assertRaises(TypeError):
            GenericDynamical(IsIrreducible())

    def test_generic_dynamical_satisfies_raises(self):
        """
        GenericDynamical.satisfies raises a TypeError when its argument is not
        a network.
        """
        allpass = GenericDynamical(lambda n: True)
        with self.assertRaises(TypeError):
            allpass.satisfies(nx.Graph())
        with self.assertRaises(TypeError):
            allpass.satisfies(nx.DiGraph())

    def test_generic_dynamical_satisfies(self):
        """
        GenericDynamical.satisfies correctly checks networks.
        """
        allpass = GenericDynamical(lambda n: True)
        self.assertTrue(allpass.satisfies(myeloid))
        self.assertTrue(allpass.satisfies(s_pombe))

        allfail = GenericDynamical(lambda g: False)
        self.assertFalse(allfail.satisfies(myeloid))
        self.assertFalse(allfail.satisfies(s_pombe))

        ninenodes = GenericDynamical(lambda g: g.size == 9)
        self.assertTrue(ninenodes.satisfies(s_pombe))
        self.assertFalse(ninenodes.satisfies(myeloid))
