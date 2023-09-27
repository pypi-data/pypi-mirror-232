import numpy as np
from sklearn.cluster import KMeans

from gridfinder.utils import get_shifted_coordinate_sets, get_grid_coordinates
from gridfinder.rotation import get_best_angle_of_rotation, rotate_coordinates

def approximate_grid(points, n_cols=16, n_rows=16, **kwargs):
    alpha = get_best_angle_of_rotation(points)

    unrotated = rotate_coordinates(points, alpha)
    
    column_cluster, row_cluster = get_shifted_coordinate_sets(unrotated)
    
    # fit KMeans algorithm to detect clusters in the shifted rows and columns
    kmrow = KMeans(n_clusters=n_rows)
    kmrow.fit(row_cluster)
    row_coordinates = kmrow.cluster_centers_[:,0]

    kmcol = KMeans(n_clusters=n_cols)
    kmcol.fit(column_cluster)
    column_coordinates = kmcol.cluster_centers_[:,1]

    # here might be an additional filtering step necessary to 
    # filter false cluster centers caused by extreme point deviations
    targetpositions = get_grid_coordinates(row_coordinates, column_coordinates)
    #targetpositions = rotate_coordinates(targetpositions, -alpha)
    return targetpositions
