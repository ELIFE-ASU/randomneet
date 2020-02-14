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
        The TopologicalConstraint should be an abstract subclass of AbstractConstraint
        """
        self.assertTrue(issubclass(rc.TopologicalConstraint, rc.AbstractConstraint))
        with self.assertRaises(TypeError):
            rc.TopologicalConstraint()

    def test_dynamical_constraint(self):
        """
        The DynamicalConstraint should be an abstract subclass of AbstractConstraint
        """
        self.assertTrue(issubclass(rc.DynamicalConstraint, rc.AbstractConstraint))
        with self.assertRaises(TypeError):
            rc.DynamicalConstraint()
