import numpy as np

from gridfinder.translation import translate_center_to_origin, get_center
from gridfinder.utils import matrix_coordinate_oriented

def get_best_angle_of_rotation(coordinates):
    """Returns the angle of rotation where the bounding box of 
    all coordinates is minimized in 0.5 degree steps."""
    alpha = 0
    area = None
    for i in np.linspace(-45,45,180):
        rot = rotate_coordinates(coordinates, i)
        min_y = np.min(rot[1,:])
        max_y = np.max(rot[1,:])
        min_x = np.min(rot[0,:])
        max_x = np.max(rot[0,:])
        area_ = (max_x-min_x) * (max_y-min_y)
        if area == None or area_ < area:
            area = area_
            alpha = i
    return alpha

def rotate_coordinates(coordinates, angle):
    """Rotates all coordinates around their center by angle (in degrees)."""
    center = get_center(coordinates)
    coordinates_at_center = translate_center_to_origin(coordinates, center)

    theta = np.deg2rad(angle)
    rotation_matrix = np.array((
        (np.cos(theta), -np.sin(theta)),
        (np.sin(theta), np.cos(theta))
    ))

    if matrix_coordinate_oriented(coordinates_at_center):
        rotated = rotation_matrix@coordinates_at_center.T
        return translate_center_to_origin(rotated, -center).T
    else:
        rotated = rotation_matrix@coordinates_at_center
        return translate_center_to_origin(rotated, -center)