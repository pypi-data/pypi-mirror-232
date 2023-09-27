import random
import numpy as np
from pystrich.datamatrix import DataMatrixEncoder

def get_code_positions(string):
    dme = DataMatrixEncoder(string)
    size = len(dme.matrix)
    if size != 14:
        raise ValueError(f'({size}, {size}) is not equal to (14, 14). \
            Change number of encodes characters')
    matrix = np.ones((size+2, size+2))
    matrix[1:-1, 1:-1] = dme.matrix
    for i in range(size+2):
        if i % 2 == 0:
            matrix[i, -1] = 0
        if i % 2 == 1:
            matrix[0, i] = 0

    return matrix

def positions2coordinates(matrix, distance):
    xy = []
    for i, row in enumerate(reversed(matrix)):
        for j, value in enumerate(row): 
            if value == 1:
                xy.append([j*distance, i*distance])
            else:
                pass
    
    return np.asarray(xy)

def shuffle_points(grid_points, mean_dev=(0, 0), std_dev=(0, 0), point_std=0):
    col_positions = dict()
    real_points = []
    for p in grid_points:
        new_point = []
        
        if p[0] not in col_positions.keys():
            neg_x = np.random.random_sample()
            col_dev_x = np.random.normal(mean_dev[0], std_dev[0])
            neg_y = np.random.random_sample()
            col_dev_y = np.random.normal(mean_dev[1], std_dev[1])
            if neg_x < 0.5: col_dev_x = -1 * col_dev_x
            else: col_dev_x = col_dev_x
            if neg_y < 0.5: col_dev_y = -1 * col_dev_y
            else: col_dev_y = col_dev_y
                
            col_positions[p[0]] = (col_dev_x, col_dev_y)
                
        for i, coord in enumerate(p):
            point_randomness = np.random.normal(0, point_std)
            new_point.append(int(p[i] + col_positions[p[0]][i] + point_randomness))
            
        real_points.append(new_point)
        
    return np.asarray(real_points)

def simulate_prints(points, n_constant, n_fading, point_std):
    grid_points = np.copy(points)
    column_positions = []
    for p in grid_points:
        if p[1] not in column_positions: column_positions.append(p[1])

    weights = []
    for p in grid_points:
        column_points = grid_points[np.where(grid_points[:,1]==p[1])]
        columnIndex = column_points.tolist().index(p.tolist())
        if columnIndex > 2:
            weights.append(1)
        else:
            weights.append(0)

    constant_shift_idxs = random.sample(range(len(column_positions)), n_constant)
    fading_shift_idxs = random.sample(range(len(column_positions)), n_fading)

    constant_shifts = [random.randint(-15, 15) for idx in constant_shift_idxs]
    fading_columns = [[] for _ in range(n_fading)]
    for i, idx in enumerate(fading_shift_idxs):
        c_value = column_positions[idx]
        for j, p in enumerate(grid_points):
            if p[1] == c_value:
                fading_columns[i].append(j)

    for fc in fading_columns:
        fc.sort()

    positive = random.choices([-1, 1], k=n_fading)

    for j, point in enumerate(grid_points):
        position_in_list = column_positions.index(point[1])

        if position_in_list in constant_shift_idxs:
            shift = constant_shifts[constant_shift_idxs.index(position_in_list)]
            point[1] += shift

        if position_in_list in fading_shift_idxs:
            index_in_column = fading_columns[fading_shift_idxs.index(position_in_list)].index(j)
            if index_in_column == 0:
                point[1] += 14 * positive[fading_shift_idxs.index(position_in_list)]
            if index_in_column == 1:
                point[1] += 7 * positive[fading_shift_idxs.index(position_in_list)]
            if index_in_column == 2:
                point[1] += 4 * positive[fading_shift_idxs.index(position_in_list)]
            
        point[0] += random.randint(-point_std, point_std)
        point[1] += random.randint(-point_std, point_std)
    return grid_points, weights
    