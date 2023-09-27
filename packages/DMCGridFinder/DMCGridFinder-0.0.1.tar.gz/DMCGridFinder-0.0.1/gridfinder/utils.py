import numpy as np

def verify_coordinate_shape(coordinates):

    if len(coordinates.shape) > 2:
        raise ValueError('Too many dimensions')

    if 2 not in coordinates.shape:
        raise ValueError('Coordinates shape should be (N, 2) or (2, N)') 

def matrix_coordinate_oriented(coordinates):
    # coordinate oriented --> (N, 2)
    # else --> (2, N)
    # if only two points are given, we assume the matrix is not coordinate oriented
    verify_coordinate_shape(coordinates)
    if coordinates.shape[0] == 2:
        return False

    if coordinates.shape[1] == 2:
        return True

def get_shifted_coordinate_sets(coordinates):
    
    coordinate_oriented = matrix_coordinate_oriented(coordinates)

    if coordinate_oriented:
        min_row_value = np.min(coordinates[:,0]) 
        min_col_value = np.min(coordinates[:,1])

        column_cluster = np.copy(coordinates)
        column_cluster[:,0] -= np.abs(coordinates[:,0]-min_row_value)

        row_cluster = np.copy(coordinates)
        row_cluster[:,1] -= np.abs(coordinates[:,1]-min_col_value)

        return column_cluster, row_cluster

    else:
        min_row_value = np.min(coordinates[0,:])
        min_col_value = np.min(coordinates[1,:])

        column_cluster = np.copy(coordinates)
        column_cluster[0,:] -= np.abs(coordinates[0,:]-min_row_value)

        row_cluster = np.copy(coordinates)
        row_cluster[1,:] -= np.abs(coordinates[1,:]-min_col_value)

        return column_cluster, row_cluster

def get_grid_coordinates(row_coordinates, column_coordinates):
    grid_points = []
    for x in column_coordinates:
        for y in row_coordinates:
            grid_points.append((y, x))

    return np.asarray(grid_points)

def get_dmc_dimension(points):
    # Shape of data matrix code based on the number of positives modules.
    # Might lead to errors if too many dots are connected and detected as 
    # a single position
    positivesModulesDict = {
        10: {'min': 49.0, 'max': 64.0},
        12: {'min': 68.0, 'max': 89.0},
        14: {'min': 94.0, 'max': 123.0},
        16: {'min': 125.0, 'max': 156.0},
        18: {'min': 153.0, 'max': 192.0},
        20: {'min': 200.0, 'max': 235.0}
    }
    
    possible_dimensions = []
    for key in positivesModulesDict.keys():
        if points.shape[0] >= positivesModulesDict[key]['min'] and \
            points.shape[0] <= positivesModulesDict[key]['max']:
            possible_dimensions.append(key)
    
    if len(possible_dimensions) == 0:
        raise ValueError('Could not detect DMC size.')
    
    return possible_dimensions
