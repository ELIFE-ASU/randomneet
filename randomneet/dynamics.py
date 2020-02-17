from .randomizer import AbstractRandomizer
from .topology import TopologyRandomizer, FixedTopology
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
        super().__init__(network, constraints, timeout)
        if trand is None:
            trand = FixedTopology(self.graph)
        elif isclass(trand) and issubclass(trand, TopologyRandomizer):
            trand = trand(self.graph)
        elif isinstance(trand, TopologyRandomizer):
            pass
        else:
            raise TypeError('trand must be an instance or subclass of TopologyRandomizer')

        self.trand = trand
