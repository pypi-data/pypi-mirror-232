import numpy as np
from scipy.optimize import minimize

from gridfinder.pattern_creator import positions2coordinates
from gridfinder.translation import get_center, translate_center_to_origin
from gridfinder.rotation import rotate_coordinates
from gridfinder.metrics import get_distances
from gridfinder.utils import get_dmc_dimension
from gridfinder.error_function import error_function


def approximate_grid(points, **kwargs):
    possible_dimensions = get_dmc_dimension(points)

    targetpositions = None
    mean_distance = None

    for size in possible_dimensions:
        targetpositions_ = np.ones((size, size))

        real_center = get_center(points)

        # approximate seed value for module size
        module_x = (np.max(points[:, 0]) -
                    np.min(points[:, 0])) / targetpositions_.shape[0]
        module_y = (np.max(points[:, 1]) -
                    np.min(points[:, 1])) / targetpositions_.shape[1]
        module_seed = np.mean([module_x, module_y])

        seed_values = (module_seed, 0)
        bounds = [(module_seed * 0.8, module_seed * 1.2), (-2, 2)]
        args = {
            'targetpositions': targetpositions_,
            'realpositions': points
        }

        res = minimize(
            lambda X: error_function(*X, **args), seed_values, bounds=bounds
        )

        # create targetpositions with optimized values
        targetpositions_ = positions2coordinates(targetpositions_, res.x[0])
        targetpositions_ = rotate_coordinates(targetpositions_, res.x[1])

        # translate targets center to origin and afterwards to the center of
        # the real positions
        targetpositions_ = translate_center_to_origin(
            targetpositions_, get_center(targetpositions_))
        targetpositions_ = translate_center_to_origin(
            targetpositions_, -real_center)

        mean_distance_ = get_distances(targetpositions_, points)
        if (mean_distance == None or mean_distance_ < mean_distance):
            mean_distance = mean_distance_
            targetpositions = targetpositions_

    return targetpositions
