import unittest
import numpy as np

from gridfinder.unguided import UGC
from gridfinder.pattern_creator import \
    get_code_positions, \
    positions2coordinates, \
    shuffle_points
from gridfinder.metrics import get_distances

string = 'IKTSDresden'

class TestUSC(unittest.TestCase):

    def test_approximate_grid(self):
        real_positions = shuffle_points(positions2coordinates(get_code_positions(string), 20))
        targets = UGC.approximate_grid(real_positions)
        self.assertTrue(real_positions.shape[1]==targets.shape[1])

    def test_approximate_grid_with_shuffling(self):
        real_positions = shuffle_points(positions2coordinates(get_code_positions(string), 20), point_std=2)
        targets = UGC.approximate_grid(real_positions)
        distances = get_distances(targets, real_positions)
        self.assertFalse(np.std(distances) > 2)
