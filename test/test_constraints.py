import networkx as nx
import randomneet
import randomneet.constraints as rc
import unittest


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
