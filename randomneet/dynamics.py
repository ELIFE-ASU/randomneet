from .randomizer import AbstractRandomizer
from .topology import TopologyRandomizer, FixedTopology
from .constraints import DynamicalConstraint, TopologicalConstraint, GenericDynamical
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
        if trand is None:
            trand = FixedTopology(network, timeout=timeout, **kwargs)
        elif isclass(trand) and issubclass(trand, TopologyRandomizer):
            trand = trand(network, timeout=timeout, **kwargs)
        elif isinstance(trand, TopologyRandomizer):
            pass
        else:
            raise TypeError('trand must be an instance or subclass of TopologyRandomizer')
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
