from gridfinder import rotation, translation

import unittest
import numpy as np

coordinates = np.array([
    [1, 2],
    [1.5, 1.5],
    [1.5, 2.5],
    [2, 1],
    [2, 3],
    [2.5, 1.5],
    [2.5, 2.5],
    [3, 2]
])

class TestRotation(unittest.TestCase):

    def test_get_best_angle_of_rotation(self):
        angle = rotation.get_best_angle_of_rotation(coordinates)
        self.assertEqual(np.abs(angle), 45)

    def test_get_best_angle_of_rotation_translated(self):
        angle = rotation.get_best_angle_of_rotation(coordinates.T)
        self.assertEqual(np.abs(angle), 45)

    def test_rotate_coordinates_center_consistent(self):
        center_before = translation.get_center(coordinates)
        rotated = rotation.rotate_coordinates(coordinates, 45)
        center_after = translation.get_center(rotated)
        self.assertTrue(np.all(center_after == center_before))

    def test_rotate_coordinates_coordinates_shape(self):
        rotated = rotation.rotate_coordinates(coordinates, 45)
        self.assertTrue(np.all(coordinates.shape == rotated.shape))