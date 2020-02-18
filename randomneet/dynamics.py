from .randomizer import AbstractRandomizer


class NetworkRandomizer(AbstractRandomizer):
    def __init__(self, network, **kwargs):
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
        super().__init__(network, **kwargs)

    def _randomize(self):
        return self.network
