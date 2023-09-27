import unittest
import numpy as np

from gridfinder.guided import GAT
from gridfinder.guided import GC
from gridfinder.pattern_creator import \
    get_code_positions, \
    positions2coordinates, \
    shuffle_points
from gridfinder.metrics import get_distances

string = 'IKTSDresden'

class TestSAT(unittest.TestCase):

    def test_approximate_grid(self):
        real_positions = shuffle_points(positions2coordinates(get_code_positions(string), 20))
        targets = GAT.approximate_grid(real_positions, string)
        self.assertTrue(real_positions.shape==targets.shape)

    def test_approximate_grid_with_shuffling(self):
        real_positions = shuffle_points(positions2coordinates(get_code_positions(string), 20), point_std=2)
        targets = GAT.approximate_grid(real_positions, string)
        distances = get_distances(targets, real_positions)
        self.assertFalse(np.std(distances) > 2)

class TestSC(unittest.TestCase):

    def test_approximate_grid(self):
        real_positions = shuffle_points(positions2coordinates(get_code_positions(string), 20))
        targets = GC.approximate_grid(real_positions)
        self.assertTrue(real_positions.shape[1]==targets.shape[1])

    def test_approximate_grid_with_shuffling(self):
        real_positions = shuffle_points(positions2coordinates(get_code_positions(string), 20), point_std=2)
        targets = GC.approximate_grid(real_positions)
        distances = get_distances(targets, real_positions)
        self.assertFalse(np.std(distances) > 2.1)