from .randomizer import AbstractRandomizer


class NetworkRandomizer(AbstractRandomizer):
    def _randomize(self):
        return self.network
