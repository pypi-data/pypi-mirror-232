import unittest

from gridfinder.pattern_creator import \
    (
        get_code_positions, 
        positions2coordinates, 
        shuffle_points
    )

class TestPatternCreator(unittest.TestCase):

    def test_code_positions_raises_error(self):
        string = 'A very long message with too many characters'
        self.assertRaises(ValueError, get_code_positions, string)

    