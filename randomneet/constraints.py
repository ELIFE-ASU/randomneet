import neet
import networkx as nx
import numpy as np
from abc import ABCMeta, abstractmethod


class ConstraintError(Exception):
    """
    A constraint was applied to an invalid object.
    """
    pass


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
        return True


class TopologicalConstraint(AbstractConstraint):
    """
    An abstract class representing a constraint on the topology of a network.
    """
    @abstractmethod
    def satisfies(self, graph):
        """
        Test a provided graph against the constraint.

        :param graph: a graph to test
        :type graph: nx.DiGraph
        :returns: ``True`` if the constraint is satisfied
        :raises TypeError: if the graph is not a networkx DiGraph
        """
        if not isinstance(graph, nx.DiGraph):
            raise TypeError('only directed graphs are testable with topological constraints')
        return super(TopologicalConstraint, self).satisfies(graph)


class DynamicalConstraint(AbstractConstraint):
    """
    An abstract class representing a constraint on the dynamics of a network.
    """
    @abstractmethod
    def satisfies(self, net):
        """
        Test a provided net against the constraint.

        :param net: a network to test
        :type net: neet.Network
        :returns: ``True`` if the constraint is satisfied
        :raises TypeError: if the network is not a neet.Network
        """
        if not isinstance(net, neet.Network):
            raise TypeError('only neet networks are testable with dynamical constraints')
        return super(DynamicalConstraint, self).satisfies(net)


class HasExternalNodes(TopologicalConstraint):
    def __init__(self, target):
        """
        An topological constraint requiring a specific number of external
        nodes, i.e. a specific number of nodes with no incomming edges.

        If ``target`` is a directed graph, this constraint will require
        networks to have the same number of external nodes as the target.
        Alternativly, ``target`` can be a non-negative integer.

        :param target: the target number of external nodes
        :type target: nx.DiGraph or integer
        """
        if isinstance(target, int):
            if target < 0:
                raise ValueError('the target number of external nodes must be non-negative')
            num_external = target
        elif isinstance(target, nx.DiGraph):
            num_external = self.__count_external(target)
        else:
            raise TypeError('target must be either an integer or nx.DiGraph')

        self.num_external = num_external

    def __count_external(self, g):
        """
        Count the number of external nodes in a directed graph.
        """
        return np.count_nonzero([d == 0 for _, d in g.in_degree()])

    def satisfies(self, graph):
        """
        This constraint is only satisfied if the provided graph as
        ``self.num_external``-many external nodes.

        :param graph: a graph to test
        :type graph: nx.DiGraph
        :returns: ``True`` if the digraph as the desired number of external
                  nodes
        """
        if super(HasExternalNodes, self).satisfies(graph):
            return self.__count_external(graph) == self.num_external


class IsConnected(TopologicalConstraint):
    """
    Ensure that the resulting graph is (weakly) connected.
    """
    def satisfies(self, graph):
        """
        This constraint is only satisfied if the provided graph as is weakly
        connected.

        :param graph: a graph to test
        :type graph: nx.DiGraph
        :returns: ``True`` if the digraph as the desired number of external
                  nodes
        """
        if super(IsConnected, self).satisfies(graph):
            try:
                return nx.is_weakly_connected(graph)
            except nx.exception.NetworkXException as err:
                raise ConstraintError() from err


class IsIrreducible(DynamicalConstraint):
    """
    Ensure that all dynamical nodes have irreducible functions.
    """
    def satisfies(self, network):
        """
        This constraint is only satisfied if every node's function logically
        depends on each of it's incoming neighbors.

        :param network: a network to test
        :type network: neet.boolean.LogicNetwork
        :returns: ``True`` if every node's function is irredicible
        """
        if super(IsIrreducible, self).satisfies(network):
            if not isinstance(network, neet.boolean.LogicNetwork):
                raise NotImplementedError('IsIrreducible is not implemented for networks of type {}'
                                          .format(type(network)))

            for idx in range(network.size):
                for neighbor_in in network.neighbors_in(idx):
                    if not network.is_dependent(idx, neighbor_in):
                        return False
            return True
