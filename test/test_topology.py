import randomneet
import unittest


class TestTopologyRandomizers(unittest.TestCase):
    """
    Unit tests for the topology randomizers
    """

    def test_topology_module(self):
        """
        Ensure that TopologyRandomizer is exported from randomneet
        """
        self.assertTrue('topology' in dir(randomneet))
