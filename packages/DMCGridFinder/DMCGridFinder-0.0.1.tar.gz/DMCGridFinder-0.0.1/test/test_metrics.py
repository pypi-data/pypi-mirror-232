from gridfinder import metrics

import unittest
import numpy as np

targetpositions = np.array([
    [1, 1],
    [1, 2],
    [1, 3],
    [2, 1],
    [2, 3],
    [3, 1],
    [3, 2],
    [3, 3]
])

approximatedpositions = np.array([
    [0.8, 1],
    [0.9, 2],
    [1, 3],
    [2, 1],
    [2, 2],
    [2, 3],
    [3.2, 1],
    [3.1, 2],
    [3, 3]
])

class TestMetrics(unittest.TestCase):

    def test_get_distances(self):
        distances = metrics.get_distances(approximatedpositions, targetpositions)
        expected_values = np.array([
            0.2,
            0.1,
            0,
            0,
            0,
            0.2,
            0.1,
            0
        ])
        self.assertTrue(np.allclose(distances, expected_values))

    def test_get_distances_shape(self):
        distances = metrics.get_distances(approximatedpositions, targetpositions)
        self.assertTrue(distances.shape[0]==targetpositions.shape[0])

    def test_get_matches(self):
        threshold = 0.1
        distances = metrics.get_distances(approximatedpositions, targetpositions)
        matches = metrics.get_matches(distances, threshold)
        self.assertEqual(matches.shape[0], 6)