from .randomizer import AbstractRandomizer
from .constraints import TopologicalConstraint, GenericTopological


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
