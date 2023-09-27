from gridfinder import translation

import unittest
import numpy as np

coordinates = np.array([
    [1, 1],
    [1, 2],
    [1, 3],
    [2, 1],
    [2, 3],
    [3, 1],
    [3, 2],
    [3, 3]
])

class TestTranslation(unittest.TestCase):

    def test_get_center(self):
        center = translation.get_center(coordinates)
        print(center)
        self.assertTrue(np.allclose(center, np.array([2, 2])))

    def test_get_center_with_transposed(self):
        coordinates_T = coordinates.T
        center_T = translation.get_center(coordinates_T)
        center = translation.get_center(coordinates)
        self.assertTrue(np.all(center_T == center))

    def test_translate_center_to_origin(self):
        center = translation.get_center(coordinates)
        translated = translation.translate_center_to_origin(coordinates, center)
        new_center = translation.get_center(translated)
        self.assertTrue(np.all(new_center == 0))

    def test_translate_center_to_origin_keeps_dimensions(self):
        center = translation.get_center(coordinates)
        translated = translation.translate_center_to_origin(coordinates.T, center)

        self.assertTrue(np.all(translated.shape == coordinates.T.shape))
