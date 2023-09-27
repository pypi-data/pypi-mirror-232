import numpy as np
from scipy.spatial.distance import cdist

def get_distances(approximatedpositions, targetpositions):
    dist_matrix = cdist(approximatedpositions, targetpositions)
    distances = np.min(dist_matrix, axis=0)
    
    return distances

def get_matches(distances, threshold):
    matches = np.where(np.round(distances, 5) <= threshold)[0]
    return matches