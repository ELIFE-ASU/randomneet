from abc import ABCMeta, abstractmethod


class AbstractConstraint(object, metaclass=ABCMeta):
    """
    An abstract class representing a constraint used for rejection testing.
    """
    @abstractmethod
    def satisfies(self, net):
        """
        Test a provided network against the constraint.

        :param net: a network to test
        :returns: ``True`` if the constraint is satisfied
        """
        pass


class TopologicalConstraint(AbstractConstraint):
    """
    An abstract class representing a constraint on the topology of a network.
    """
    @abstractmethod
    def satisfies(self, net):
        """
        Test a provided network against the constraint.

        :param net: a network to test
        :returns: ``True`` if the constraint is satisfied
        """
        pass


class DynamicalConstraint(AbstractConstraint):
    """
    An abstract class representing a constraint on the dynamics of a network.
    """
    @abstractmethod
    def satisfies(self, net):
        """
        Test a provided network against the constraint.

        :param net: a network to test
        :returns: ``True`` if the constraint is satisfied
        """
        pass
