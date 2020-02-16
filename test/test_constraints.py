import networkx as nx
import randomneet
import randomneet.constraints as rc
import unittest

from neet.boolean import LogicNetwork
from neet.boolean.examples import s_pombe, myeloid


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
        self.assertTrue(issubclass(rc.AbstractConstraint, object))
        with self.assertRaises(TypeError):
            rc.AbstractConstraint()  # type: ignore

    def test_topological_constraint(self):
        """
        The TopologicalConstraint should be an abstract subclass of
        AbstractConstraint
        """
        self.assertTrue(issubclass(rc.TopologicalConstraint, rc.AbstractConstraint))
        with self.assertRaises(TypeError):
            rc.TopologicalConstraint()  # type: ignore

    def test_dynamical_constraint(self):
        """
        The DynamicalConstraint should be an abstract subclass of
        AbstractConstraint
        """
        self.assertTrue(issubclass(rc.DynamicalConstraint, rc.AbstractConstraint))
        with self.assertRaises(TypeError):
            rc.DynamicalConstraint()  # type: ignore

    def test_has_external_nodes_is_topological(self):
        """
        The HasExternalNodes constraint is a TopologicalConstraint
        """
        self.assertTrue(issubclass(rc.HasExternalNodes, rc.TopologicalConstraint))

    def test_has_external_nodes_invalid_init(self):
        """
        HasExternalNodes should raise a Value or TypeError for invalid
        initialization parameters.
        """
        with self.assertRaises(ValueError):
            rc.HasExternalNodes(-1)
        with self.assertRaises(TypeError):
            rc.HasExternalNodes(nx.Graph())

    def test_has_external_nodes_counts(self):
        """
        HasExternalNodes properly counts the number of external nodes in a
        directed graph.
        """
        g = nx.DiGraph([(0, 1), (1, 2), (2, 1), (3, 1), (4, 5), (6, 6)])
        constraint = rc.HasExternalNodes(g)
        self.assertEqual(constraint.num_external, 3)

    def test_has_external_nodes_saves_target(self):
        """
        HasExternalNodes properly stores the desired number of external edges.
        """
        self.assertEqual(rc.HasExternalNodes(7).num_external, 7)

    def test_has_external_nodes_raises(self):
        """
        HasExternalNodes.satisfies raises an error if the provided argument is
        not a directed graph.
        """
        constraint = rc.HasExternalNodes(3)
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

        constraint = rc.HasExternalNodes(3)
        self.assertFalse(constraint.satisfies(nx.DiGraph()))
        self.assertFalse(constraint.satisfies(nx.DiGraph([(0, 1), (1, 2), (2, 1), (3, 2)])))
        self.assertTrue(constraint.satisfies(g))

        constraint = rc.HasExternalNodes(g)
        self.assertFalse(constraint.satisfies(nx.DiGraph()))
        self.assertFalse(constraint.satisfies(nx.DiGraph([(0, 1), (1, 2), (2, 1), (3, 2)])))
        self.assertTrue(constraint.satisfies(g))
        self.assertTrue(constraint.satisfies(nx.DiGraph([(1, 2), (3, 4), (5, 6), (7, 7)])))

    def test_is_connected_is_topological(self):
        """
        The IsConnected constraint is a TopologicalConstraint
        """
        self.assertTrue(issubclass(rc.IsConnected, rc.TopologicalConstraint))

    def test_is_connected_raises(self):
        """
        IsConnected.satisfies raises an error if the provided argument is not a
        directed graph.
        """
        constraint = rc.HasExternalNodes(3)
        with self.assertRaises(TypeError):
            constraint.satisfies(3)
        with self.assertRaises(TypeError):
            constraint.satisfies(nx.Graph())

    def test_is_connected_null_graph(self):
        """
        IsConnected.satisfies raises an error if the provided argument is the
        null graph.
        """
        constraint = rc.IsConnected()
        with self.assertRaises(rc.ConstraintError):
            constraint.satisfies(nx.DiGraph())

    def test_is_connected_satisfies(self):
        """
        IsConnected.satisfies correctly identifies directed graphs that are
        weakly connected.
        """
        constraint = rc.IsConnected()
        self.assertTrue(constraint.satisfies(self.empty_graph(1)))
        self.assertTrue(constraint.satisfies(nx.DiGraph([(0, 0)])))
        self.assertFalse(constraint.satisfies(self.empty_graph(2)))
        self.assertFalse(constraint.satisfies(nx.DiGraph([(0, 0), (1, 1)])))
        self.assertTrue(constraint.satisfies(nx.DiGraph([(0, 1)])))

    def test_is_irreducibile_is_dynamical(self):
        """
        The IsIrreducible constraint is a DynamicalConstraint.
        """
        self.assertTrue(issubclass(rc.IsIrreducible, rc.DynamicalConstraint))

    def test_is_irreducible_raises(self):
        """
        IsIrreducible.satisfies raises an error if the argument is not a Neet
        network.
        """
        constraint = rc.IsIrreducible()
        with self.assertRaises(TypeError):
            constraint.satisfies(nx.DiGraph())
        with self.assertRaises(TypeError):
            constraint.satisfies(nx.Graph())

    def test_is_irreducible_satisfies_non_logic(self):
        """
        IsIrreducible.satisfies is not implemented for non-LogicNetworks
        """
        constraint = rc.IsIrreducible()
        with self.assertRaises(NotImplementedError):
            constraint.satisfies(s_pombe)

    def test_is_irreducible_satisfies(self):
        """
        IsIrreducible.satisfies correctly identifies networks that are
        irreducible.
        """
        constraint = rc.IsIrreducible()
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
        self.assertTrue(issubclass(rc.HasCanalizingNodes, rc.DynamicalConstraint))

    def test_has_canalizing_nodes_invalid_init(self):
        """
        HasCanalizingNodes should raise a ValueError or TypeError for invalid
        initialization parameters.
        """
        with self.assertRaises(ValueError):
            rc.HasCanalizingNodes(-1)
        with self.assertRaises(TypeError):
            rc.HasCanalizingNodes(nx.Graph())

    def test_has_canalizing_nodes_counts(self):
        """
        HasCanalizingNodes properly counts the number of canalizing nodes in a
        network.
        """
        constraint = rc.HasCanalizingNodes(myeloid)
        self.assertEqual(constraint.num_canalizing, 11)

        constraint = rc.HasCanalizingNodes(s_pombe)
        self.assertEqual(constraint.num_canalizing, 5)

    def test_has_canalizing_nodes_saves_target(self):
        """
        HasCanalizingNodes properly stores the desired number of external
        edges.
        """
        self.assertEqual(rc.HasCanalizingNodes(7).num_canalizing, 7)

    def test_has_canalizing_nodes_raises(self):
        """
        HasCanalizingNodes.satisfies raises an error if the provided argument
        is not a neet network
        """
        constraint = rc.HasCanalizingNodes(3)
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
        constraint = rc.HasCanalizingNodes(myeloid)
        self.assertTrue(constraint.satisfies(myeloid))
        self.assertFalse(constraint.satisfies(s_pombe))

    def test_generic_topological_is_topological(self):
        """
        Ensure that GenericTopological is a subclass of TopologicalConstraint.
        """
        self.assertTrue(issubclass(rc.GenericTopological, rc.TopologicalConstraint))

    def test_generic_topological_raises(self):
        """
        GenericTopological raises a TypeError if it's instantiated with
        anything that is not callable.
        """
        with self.assertRaises(TypeError):
            rc.GenericTopological(5)
        with self.assertRaises(TypeError):
            rc.GenericTopological(rc.IsConnected())

    def test_generic_topological_satisfies_raises(self):
        """
        GenericTopological.satisfies raises a TypeError when its argument is
        not a directed graph.
        """
        allpass = rc.GenericTopological(lambda g: True)
        with self.assertRaises(TypeError):
            allpass.satisfies(nx.Graph())
        with self.assertRaises(TypeError):
            allpass.satisfies(s_pombe)

    def test_generic_topological_satisfies(self):
        """
        GenericTopological.satisfies correctly checks graphs.
        """
        allpass = rc.GenericTopological(lambda g: True)
        self.assertTrue(allpass.satisfies(self.empty_graph()))
        self.assertTrue(allpass.satisfies(nx.DiGraph([(0, 1), (1, 2), (2, 0)])))

        allfail = rc.GenericTopological(lambda g: False)
        self.assertFalse(allfail.satisfies(self.empty_graph()))
        self.assertFalse(allfail.satisfies(nx.DiGraph([(0, 1), (1, 2), (2, 0)])))

        twonodes = rc.GenericTopological(lambda g: len(g) == 2)
        self.assertFalse(twonodes.satisfies(self.empty_graph()))
        self.assertTrue(twonodes.satisfies(self.empty_graph(2)))

    def test_generic_dynamical_is_dynamical(self):
        """
        Ensure that GenericDynamical is a subclass of DynamicalConstraint.
        """
        self.assertTrue(issubclass(rc.GenericDynamical, rc.DynamicalConstraint))

    def test_generic_dynamical_raises(self):
        """
        GenericDynamical raises a TypeError if it's instantiated with anything
        that is not callable.
        """
        with self.assertRaises(TypeError):
            rc.GenericDynamical(5)
        with self.assertRaises(TypeError):
            rc.GenericDynamical(rc.IsIrreducible())

    def test_generic_dynamical_satisfies_raises(self):
        """
        GenericDynamical.satisfies raises a TypeError when its argument is not
        a network.
        """
        allpass = rc.GenericDynamical(lambda n: True)
        with self.assertRaises(TypeError):
            allpass.satisfies(nx.Graph())
        with self.assertRaises(TypeError):
            allpass.satisfies(nx.DiGraph())

    def test_generic_dynamical_satisfies(self):
        """
        GenericDynamical.satisfies correctly checks networks.
        """
        allpass = rc.GenericDynamical(lambda n: True)
        self.assertTrue(allpass.satisfies(myeloid))
        self.assertTrue(allpass.satisfies(s_pombe))

        allfail = rc.GenericDynamical(lambda g: False)
        self.assertFalse(allfail.satisfies(myeloid))
        self.assertFalse(allfail.satisfies(s_pombe))

        ninenodes = rc.GenericDynamical(lambda g: g.size == 9)
        self.assertTrue(ninenodes.satisfies(s_pombe))
        self.assertFalse(ninenodes.satisfies(myeloid))
