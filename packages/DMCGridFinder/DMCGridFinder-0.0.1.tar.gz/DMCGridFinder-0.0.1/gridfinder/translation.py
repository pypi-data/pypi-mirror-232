import numpy as np
from gridfinder.utils import matrix_coordinate_oriented

def get_center(coordinates):
    """Returns the center of all coordinates."""
    if matrix_coordinate_oriented(coordinates):
        mean_row = np.min(coordinates[:,0]) + (np.max(coordinates[:,0]) - np.min(coordinates[:,0])) / 2
        mean_col = np.min(coordinates[:,1]) + (np.max(coordinates[:,1]) - np.min(coordinates[:,1])) / 2
        return np.array([mean_row, mean_col])
    else:
        mean_row = np.min(coordinates[0,:]) + (np.max(coordinates[0,:]) - np.min(coordinates[0,:])) / 2
        mean_col = np.min(coordinates[1,:]) + (np.max(coordinates[1,:]) - np.min(coordinates[1,:])) / 2
        return np.array([mean_row, mean_col])

def translate_center_to_origin(coordinates, center):
    """Shifts all coordinates, so that the center is
    in the origin of the coordinate system."""
    if coordinates.shape[0] == 2:
        coordinates = coordinates.T

        translated = coordinates - center
        return translated.T
    
    else: 
        return coordinates - center

