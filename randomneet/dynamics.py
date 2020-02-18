import neet
import numpy as np

from abc import abstractmethod
from .randomizer import AbstractRandomizer
from .topology import TopologyRandomizer, FixedTopology
from .constraints import DynamicalConstraint, TopologicalConstraint, GenericDynamical, ConstraintError
from inspect import isclass


class NetworkRandomizer(AbstractRandomizer):
    def __init__(self, network, trand=None, constraints=None, timeout=1000, **kwargs):
        """
        An abstract base class for all randomizers which implement dynamical
        randomization.

        :param network: a base network or graph
        :type network: neet.Network or networkx.DiGraph
        :param trand: how to randomize the topology (default: FixedTopology)
        :type trand: instance or subclass of TopologyRandomizer, or None
        :param constraints: constraints used for rejection testing
        :type constraints: a sequence of AbstractConstraint instances
        :param timeout: the number of attempts before rejection testing times
                        out. If less than 1, the rejection testing will never
                        time out.
        """
        #  if trand is None:
        #      trand = FixedTopology(network, timeout=timeout, **kwargs)
        #  elif isclass(trand) and issubclass(trand, TopologyRandomizer):
        #      trand = trand(network, timeout=timeout, **kwargs)
        #  elif isinstance(trand, TopologyRandomizer):
        #      pass
        #  else:
        #      raise TypeError('trand must be an instance or subclass of TopologyRandomizer')
        self.trand = trand
        super().__init__(network, constraints, timeout, **kwargs)

    @property
    def constraints(self):
        return super().constraints

    @constraints.setter
    def constraints(self, constraints):
        """
        Set the randomizer's constraints.

        :param constraints: the new constraints
        :type constraints: a seq of AbstractConstraint instances
        :raises TypeError: if any of the contraints are not an AbstractConstraint
        """
        if constraints is None:
            constraints = []
        elif not isinstance(constraints, list):
            constraints = list(constraints)

        tconstraints, dconstraints = [], []

        for i, constraint in enumerate(constraints):
            if isinstance(constraint, DynamicalConstraint):
                dconstraints.append(constraint)
            elif isinstance(constraint, TopologicalConstraint):
                tconstraints.append(constraint)
            elif callable(constraint):
                dconstraints.append(GenericDynamical(constraint))
            else:
                msg = 'constraints must be callable, a DynamicalConstraint or TopologicalConstraint'
                raise TypeError(msg)

        self.trand.constraints = tconstraints
        AbstractRandomizer.constraints.__set__(self, dconstraints)  # type: ignore

    def add_constraint(self, constraint):
        """
        Append a constraint to the randomizer's list of constraints.

        :param constraint: the new constraint
        :type constraint: AbstractConstraint
        :raises TypeError: if the constraint is not an AbstractConstraint
        """
        if isinstance(constraint, DynamicalConstraint):
            super().add_constraint(constraint)
        elif callable(constraint):
            super().add_constraint(GenericDynamical(constraint))
        elif isinstance(constraint, TopologicalConstraint):
            self.trand.add_constraint(constraint)
        else:
            msg = 'constraints must be callable, a DynamicalConstraint or TopologicalConstraint'
            raise TypeError(msg)

    def random(self):
        topology = self.trand.random()

        loop = 0
        while self.timeout <= 0 or loop < self.timeout:
            net = self._randomize(topology)
            if self._check_constraints(net):
                return net
            loop += 1
        raise ConstraintError('failed to generate a network that statisfies all constraints')

    def _randomize(self, topology):
        table = []
        for node in topology.nodes:
            predecessors = tuple(topology.predecessors(node))
            params = self._function_class_parameters(topology, node)
            table.append((predecessors, self._random_function(**params)))
        return neet.boolean.LogicNetwork(table)

    def _random_function(self, k, p, **kwargs):
        volume = 2**k
        integer, decimal = divmod(p * volume, 1)
        num_states = int(integer + np.random.choice(2, p=[1 - decimal, decimal]))
        indices = np.random.choice(volume, num_states, replace=False)
        return set('{0:0{1}b}'.format(index, k) for index in indices)

    @abstractmethod
    def _function_class_parameters(self, topology, node):
        return {'topology': topology, 'node': node, 'k': topology.in_degree(node)}


class UniformBias(NetworkRandomizer):
    def __init__(self, network, p=0.5, **kwargs):
        """
        Generate random Boolean networks with the same bias on each non-external
        node.
        """
        super().__init__(network, **kwargs)
        self.p = p

    def _function_class_parameters(self, topology, node):
        params = super()._function_class_parameters(topology, node)
        params.update({'p': self.p})
        return params


class MeanBias(UniformBias):
    def __init__(self, network, **kwargs):
        """
        Generate random Boolean networks with the same mean bias (on average)
        as the original network.
        """
        if not isinstance(network, neet.boolean.LogicNetwork):
            raise NotImplementedError()
        super().__init__(network, self._mean_bias(network), **kwargs)

    def _mean_bias(self, network):
        """
        Get the mean bias of a network
        """
        return np.mean([float(len(row[1]) / 2**len(row[0])) for row in network.table])
