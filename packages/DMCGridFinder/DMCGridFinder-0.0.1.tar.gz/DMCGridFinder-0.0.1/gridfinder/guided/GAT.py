import numpy as np
from scipy.optimize import minimize

from gridfinder.pattern_creator import get_code_positions, positions2coordinates
from gridfinder.translation import get_center, translate_center_to_origin
from gridfinder.rotation import rotate_coordinates
from gridfinder.metrics import get_distances
from gridfinder.error_function import error_function

def approximate_grid(points, string=None, weights=None, **kwargs):
    
    targetpositions = get_code_positions(string)

    real_center = get_center(points)

    # approximate seed value for module size
    module_x = (np.max(points[:,0]) - np.min(points[:,0])) / targetpositions.shape[0]
    module_y = (np.max(points[:,1]) - np.min(points[:,1])) / targetpositions.shape[1]
    module_seed = np.mean([module_x, module_y])

    seed_values = (module_seed, 0)
    bounds = [(module_seed * 0.8, module_seed * 1.2), (-2, 2)]
    args = {
        'targetpositions': targetpositions,
        'realpositions': points,
        'weights': weights,
    }

    res = minimize(
        lambda X: error_function(*X, **args), seed_values, bounds=bounds
    )

    # create targetpositions with optimized values
    targetpositions = positions2coordinates(targetpositions, res.x[0])
    targetpositions = rotate_coordinates(targetpositions, res.x[1])

    # translate targets center to origin and afterwards to the center of 
    # the real positions
    targetpositions = translate_center_to_origin(targetpositions, get_center(targetpositions))
    targetpositions = translate_center_to_origin(targetpositions, -real_center)

    return targetpositions
