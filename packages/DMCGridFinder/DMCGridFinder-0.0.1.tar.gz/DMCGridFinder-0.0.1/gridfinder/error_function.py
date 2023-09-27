import numpy as np
from gridfinder.pattern_creator import positions2coordinates
from gridfinder.translation import get_center, translate_center_to_origin
from gridfinder.rotation import rotate_coordinates
from gridfinder.metrics import get_distances

def error_function(module_size, alpha, targetpositions, realpositions, weights=None):
        targetpositions = positions2coordinates(targetpositions, module_size)
        target_center = get_center(targetpositions)
        real_center = get_center(realpositions)

        targets_at_center = translate_center_to_origin(targetpositions, target_center)
        real_at_center = translate_center_to_origin(realpositions, real_center)

        targets_rotated = rotate_coordinates(targets_at_center, alpha)

        return np.average(get_distances(targets_rotated, real_at_center), weights=weights)
