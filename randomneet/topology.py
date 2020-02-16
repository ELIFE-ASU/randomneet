from .randomizer import AbstractRandomizer
from .constraints import TopologicalConstraint, GenericTopological, ConstraintError


class TopologyRandomizer(AbstractRandomizer):
    """
    An abstract base class for all randomizers which implement topological
    randomization.
    """
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

        for i, constraint in enumerate(constraints):
            if isinstance(constraint, TopologicalConstraint):
                pass
            elif callable(constraint):
                constraints[i] = GenericTopological(constraint)
            else:
                raise TypeError('constraints must be callable or type TopologicalConstraint')

        AbstractRandomizer.constraints.__set__(self, constraints)  # type: ignore

    def add_constraint(self, constraint):
        """
        Append a constraint to the randomizer's list of constraints.

        :param constraint: the new constraint
        :type constraint: TopologicalConstraint
        :raises TypeError: if the constraint is not an TopologicalConstraint
        """
        if isinstance(constraint, TopologicalConstraint):
            pass
        elif callable(constraint):
            constraint = GenericTopological(constraint)
        else:
            raise TypeError('constraints must be callable or type TopologicalConstraint')

        super().add_constraint(constraint)


class FixedTopology(TopologyRandomizer):
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

        for i, constraint in enumerate(constraints):
            if isinstance(constraint, TopologicalConstraint):
                pass
            elif callable(constraint):
                constraints[i] = GenericTopological(constraint)
            else:
                raise TypeError('constraints must be callable or type TopologicalConstraint')
            if not constraints[i].satisfies(self.graph):
                msg = 'the provided network is inconsistent with the provided constraints'
                raise ConstraintError(msg)

        TopologyRandomizer.constraints.__set__(self, constraints)  # type: ignore

    def add_constraint(self, constraint):
        """
        Append a constraint to the randomizer's list of constraints.

        :param constraint: the new constraint
        :type constraint: TopologicalConstraint
        :raises TypeError: if the constraint is not an TopologicalConstraint
        """
        if isinstance(constraint, TopologicalConstraint):
            pass
        elif callable(constraint):
            constraint = GenericTopological(constraint)
        else:
            raise TypeError('constraints must be callable or type TopologicalConstraint')

        if not constraint.satisfies(self.graph):
            msg = 'the provided network is inconsistent with the provided constraints'
            raise ConstraintError(msg)

        super().add_constraint(constraint)

    def random(self):
        """
        Create a random network variant. Because we check the constraints
        against the randomizer's graph when they are added, and we are just
        returning the graph, we can be certain that this will always succeed.
        That is, this method **will not** raise a ``ConstraintError``.

        :returns: a random network or graph
        """
        return self._randomize()

    def _randomize(self):
        """
        Return a graph that is isomorphic to the desired graph.

        :returns: networkx.DiGraph
        """
        return self.graph
