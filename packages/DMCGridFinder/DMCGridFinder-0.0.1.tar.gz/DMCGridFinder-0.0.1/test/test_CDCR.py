import unittest
import numpy as np

from gridfinder.unguided import CDCR
from gridfinder.pattern_creator import get_code_positions, positions2coordinates

coordinates = np.array([
    [1, 1],
    [1, 2],
    [1, 3],
    [1, 4],
    [2, 5],
    [3, 5],
    [4, 5],
    [5, 5],
    [5, 4],
    [5, 3],
    [5, 2],
    [4, 1],
    [3, 1],
    [2, 1]
])

# we always work with [row, column] coordinates
coordinates = np.array([[c[1], c[0]] for c in coordinates])


class TestContour(unittest.TestCase):

    def test_Contour_init(self):
        contour = CDCR.Contour(coordinates)
        TL_expected = 0
        TR_expected = 11
        BL_expected = 4
        BR_expected = 7
        LT_expected = 0
        LB_expected = 3
        RT_expected = 10
        RB_expected = 7
        expected = [
            TL_expected, 
            TR_expected,
            BL_expected,
            BR_expected,
            LT_expected,
            LB_expected,
            RT_expected,
            RB_expected
        ]
        actual = [
            contour.TL,
            contour.TR,
            contour.BL,
            contour.BR,
            contour.LT,
            contour.LB,
            contour.RT,
            contour.RB
        ]
        self.assertTrue(np.all(expected==actual))

    def test_longestDistance(self):
        contour = CDCR.Contour(coordinates)
        actual = contour.longestDistance()
        expected = np.sqrt(32)
        self.assertAlmostEqual(expected, actual)

class TestCDCR(unittest.TestCase):

    def test_shift_line_by_fixed_amount_vertical(self):
        image = np.zeros((20, 20))
        image[5:15, 5:15] = 1

        start = [2, 2]
        end = [17, 4]

        start, end = CDCR.shift_line(start, end, image, 3)
        self.assertTrue(np.all(start==[2, 5]) and np.all(end==[17, 7]))

    def test_shift_line_by_fixed_amount_horizontal(self):
        image = np.zeros((20, 20))
        image[5:15, 5:15] = 1

        start = [2, 2]
        end = [4, 17]

        start, end = CDCR.shift_line(start, end, image, 3)
        self.assertTrue(np.all(start==[5, 2]) and np.all(end==[7, 17]))

    def test_shift_line_by_fixed_amount_verticalnegativ(self):
        image = np.zeros((20, 20))
        image[5:15, 5:15] = 1

        start = [2, 18]
        end = [17, 18]

        start, end = CDCR.shift_line(start, end, image, 3)
        self.assertTrue(np.all(start==[2, 15]) and np.all(end==[17, 15]))

    def test_shift_line_until_overlap_left2right(self):
        image = np.zeros((20, 20))
        image[5:15, 5:15] = 1

        start = [5, 2]
        end = [15, 2]

        start, end = CDCR.shift_line(start, end, image)
        self.assertTrue(np.all(start==(5, 5)) and np.all(end==(15, 5)))

    def test_shift_line_until_overlap_right2left(self):
        image = np.zeros((20, 20))
        image[5:15, 5:15] = 1

        start = [5, 16]
        end = [15, 16]

        start, end = CDCR.shift_line(start, end, image)
        self.assertTrue(np.all(start==(5, 14)) and np.all(end==(15, 14)))

    def test_shift_line_until_overlap_top2bottom(self):
        image = np.zeros((20, 20))
        image[5:15, 5:15] = 1

        start = [2, 5]
        end = [2, 15]

        start, end = CDCR.shift_line(start, end, image)
        self.assertTrue(np.all(start==(5, 5)) and np.all(end==(5, 15)))

    def test_shift_line_until_overlap_bottom2top(self):
        image = np.zeros((20, 20))
        image[5:15, 5:15] = 1

        start = [16, 5]
        end = [16, 15]

        start, end = CDCR.shift_line(start, end, image)
        self.assertTrue(np.all(start==(14, 5)) and np.all(end==(14, 15)))

    def test_approximate_grid_returns_correct_format(self):
        string = 'IKTSDresden'
        code_positions = get_code_positions(string)
        coordinates = positions2coordinates(code_positions, 30)
        grid = CDCR.approximate_grid(coordinates)
        self.assertTrue(grid.shape[1]==2)
