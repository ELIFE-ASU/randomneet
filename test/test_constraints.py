import networkx as nx
import randomneet
import randomneet.constraints as rc
import unittest


class TestConstraints(unittest.TestCase):
    """
    Unit tests for the various network constraints.
    """

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
            rc.AbstractConstraint()

    def test_topological_constraint(self):
        """
        The TopologicalConstraint should be an abstract subclass of
        AbstractConstraint
        """
        self.assertTrue(issubclass(rc.TopologicalConstraint, rc.AbstractConstraint))
        with self.assertRaises(TypeError):
            rc.TopologicalConstraint()

    def test_dynamical_constraint(self):
        """
        The DynamicalConstraint should be an abstract subclass of
        AbstractConstraint
        """
        self.assertTrue(issubclass(rc.DynamicalConstraint, rc.AbstractConstraint))
        with self.assertRaises(TypeError):
            rc.DynamicalConstraint()

    def test_fixed_external_nodes_invalid_init(self):
        """
        FixExternalNodes should raise a Value or TypeError for invalid
        initialization parameters.
        """
        with self.assertRaises(ValueError):
            rc.FixExternalNodes(-1)
        with self.assertRaises(TypeError):
            rc.FixExternalNodes(nx.Graph())

    def test_fixed_external_nodes_counts(self):
        """
        FixExternalNodes properly counts the number of external nodes in a
        directed graph.
        """
        g = nx.DiGraph([(0, 1), (1, 2), (2, 1), (3, 1), (4, 5), (6, 6)])
        constraint = rc.FixExternalNodes(g)
        self.assertEqual(constraint.num_external, 3)

    def test_fixed_external_nodes_saves_target(self):
        """
        FixExternalNodes properly stores the desired number of external edges.
        """
        self.assertEqual(rc.FixExternalNodes(7).num_external, 7)

    def test_fixed_external_nodes_raises(self):
        """
        FixExternalNodes.satisfies raises an error if the provided argument is
        not a directed graph.
        """
        constraint = rc.FixExternalNodes(3)
        with self.assertRaises(TypeError):
            constraint.satisfies(3)
        with self.assertRaises(TypeError):
            constraint.satisfies(nx.Graph())

    def test_fixed_external_nodes_satisfies(self):
        """
        FixExternalNodes.satsified correctly identifies directed graphs with
        the desired number of external nodes.
        """
        g = nx.DiGraph([(0, 1), (1, 2), (2, 1), (3, 1), (4, 5), (6, 6)])

        constraint = rc.FixExternalNodes(3)
        self.assertFalse(constraint.satisfies(nx.DiGraph()))
        self.assertFalse(constraint.satisfies(nx.DiGraph([(0, 1), (1, 2), (2, 1), (3, 2)])))
        self.assertTrue(constraint.satisfies(g))

        constraint = rc.FixExternalNodes(g)
        self.assertFalse(constraint.satisfies(nx.DiGraph()))
        self.assertFalse(constraint.satisfies(nx.DiGraph([(0, 1), (1, 2), (2, 1), (3, 2)])))
        self.assertTrue(constraint.satisfies(g))
        self.assertTrue(constraint.satisfies(nx.DiGraph([(1, 2), (3, 4), (5, 6), (7, 7)])))
