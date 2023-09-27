import numpy as np
from sklearn.cluster import MeanShift

from gridfinder.utils import get_shifted_coordinate_sets, get_grid_coordinates
from gridfinder.rotation import get_best_angle_of_rotation, rotate_coordinates

def approximate_grid(points, **kwargs):
    alpha = get_best_angle_of_rotation(points)

    unrotated = rotate_coordinates(points, alpha)
    
    column_cluster, row_cluster = get_shifted_coordinate_sets(unrotated)

    # sort the cluster coordinates and find the mean and the std of the distances
    sorted_row = sorted(row_cluster[:,0])
    sorted_row_diff = [sorted_row[i]-sorted_row[i-1] for i in range(1, len(sorted_row))]
    mean_row = np.mean(sorted_row_diff)
    std_row = np.std(sorted_row_diff)

    sorted_col = sorted(column_cluster[:,1])
    sorted_col_diff = [sorted_col[i]-sorted_col[i-1] for i in range(1, len(sorted_col))]
    mean_col = np.mean(sorted_col_diff)
    std_col = np.std(sorted_col_diff)

    # fit KMeans algorithm to detect clusters in the shifted rows and columns
    msrow = MeanShift(bandwidth=mean_row+1.5*std_row)
    msrow.fit(row_cluster)
    row_coordinates = msrow.cluster_centers_[:,0]

    mscol = MeanShift(bandwidth=mean_col+1.5*std_col)
    mscol.fit(column_cluster)
    column_coordinates = mscol.cluster_centers_[:,1]

    # here might be an additional filtering step necessary to 
    # filter false cluster centers caused by extreme point deviations

    targetpositions = get_grid_coordinates(row_coordinates, column_coordinates)
    targetpositions = rotate_coordinates(targetpositions, -alpha)
    return targetpositions