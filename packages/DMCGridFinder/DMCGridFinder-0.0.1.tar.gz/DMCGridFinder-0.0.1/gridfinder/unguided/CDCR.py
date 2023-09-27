import sys
import time
import numpy as np
from skimage.draw import disk, polygon, line
from skimage.measure import label, regionprops
from scipy import ndimage
from scipy.spatial.distance import cdist
from collections import namedtuple

def create_image(coordinates):
    coordinates = coordinates + 50
    max_dimension = np.max(coordinates)
    image = np.zeros((max_dimension+50, max_dimension+50))
    for i in range(coordinates.shape[0]):
        rr, cc = disk(coordinates[i], 12)
        image[rr, cc] = 1
    return image

def connect_dots(image, stick_size):
    output_image = np.zeros_like(image)

    for row in range(int(stick_size / 2), int(image.shape[0] - stick_size / 2) - 1):
        for column in range(int(stick_size / 2), int(image.shape[1] - stick_size / 2) - 1):
            if (row == None):
                break
            
            if image[row, column] == 1:
                output_image[row, column] = 1
                continue
            else:
                left_pixel = image[row, int(column - stick_size / 2)]
                right_pixel = image[row, int(column + stick_size / 2)]
                top_pixel = image[int(row - stick_size / 2), column]
                bottom_pixel = image[int(row + stick_size / 2), column]

                if (left_pixel and right_pixel) or (top_pixel and bottom_pixel):
                    if (left_pixel and right_pixel):
                        for i in range(int(column - stick_size / 2) + 1, int(column + stick_size / 2) - 1):
                            output_image[row, i] = 1
                    if (top_pixel and bottom_pixel):
                        for i in range(int(row - stick_size / 2) + 1, int(row + stick_size / 2) - 1):
                            output_image[i, column] = 1
                else:
                    continue
    
    return output_image

def distance(coordinate1, coordinate2):
    return np.sqrt((coordinate1[0] - coordinate2[0])**2 + (coordinate1[1] - coordinate2[1])**2)


class Contour:

    def __init__(self, coordinates):
        self.coordinates = coordinates
        
        top_coordinates_idx = np.where(self.coordinates[:,0]==np.min(self.coordinates[:,0]))[0]
        bottom_coordinates_idx = np.where(self.coordinates[:,0]==np.max(self.coordinates[:,0]))[0]
        left_coordinates_idx = np.where(self.coordinates[:,1]==np.min(self.coordinates[:,1]))[0]
        right_coordinates_idx = np.where(self.coordinates[:,1]==np.max(self.coordinates[:,1]))[0]

        top_coordinates = self.coordinates[top_coordinates_idx]
        self.TL = top_coordinates_idx[np.where(top_coordinates[:,1]==np.min(top_coordinates[:,1]))][0]
        self.TR = top_coordinates_idx[np.where(top_coordinates[:,1]==np.max(top_coordinates[:,1]))][0]
        
        bottom_coordinates = self.coordinates[bottom_coordinates_idx]
        self.BL = bottom_coordinates_idx[np.where(bottom_coordinates[:,1]==np.min(bottom_coordinates[:,1]))][0]
        self.BR = bottom_coordinates_idx[np.where(bottom_coordinates[:,1]==np.max(bottom_coordinates[:,1]))][0]

        left_coordinates = self.coordinates[left_coordinates_idx]
        self.LT = left_coordinates_idx[np.where(left_coordinates[:,0]==np.min(left_coordinates[:,0]))][0]
        self.LB = left_coordinates_idx[np.where(left_coordinates[:,0]==np.max(left_coordinates[:,0]))][0]

        right_coordinates = self.coordinates[right_coordinates_idx]
        self.RT = right_coordinates_idx[np.where(right_coordinates[:,0]==np.min(right_coordinates[:,0]))][0]
        self.RB = right_coordinates_idx[np.where(right_coordinates[:,0]==np.max(right_coordinates[:,0]))][0]

    def longestDistance(self):
        points = np.asarray([
            self.coordinates[self.TL], 
            self.coordinates[self.TR], 
            self.coordinates[self.BL], 
            self.coordinates[self.BR], 
            self.coordinates[self.LT], 
            self.coordinates[self.LB], 
            self.coordinates[self.RT], 
            self.coordinates[self.RB]
        ])
        
        longest_distance = None
        return np.max(cdist(points, points))

def lineOverlap(coordinate1, coordinate2, image):
    if coordinate1[0] >= image.shape[0]:
        coordinate1[0] = image.shape[0] -1
    if coordinate2[0] >= image.shape[0]:
        coordinate2[0] = image.shape[0] -1
    if coordinate1[1] >= image.shape[1]:
        coordinate1[1] = image.shape[1] -1 
    if coordinate2[1] >= image.shape[1]:
        coordinate2[1] = image.shape[1] -1

    positives = 0
    negatives = 0

    rr, cc = line(
        coordinate1[0], 
        coordinate1[1], 
        coordinate2[0], 
        coordinate2[1]
    )

    positives = np.sum(image[rr, cc])
    negatives = rr.shape[0] - positives

    return positives / (positives + negatives) 

def midpoint(coordinate1, coordinate2):
    row = int((coordinate1[0] +  coordinate2[0]) / 2)
    col = int((coordinate1[1] + coordinate2[1]) / 2)
    return (row, col) 

def find_orientation(image):
    img_center_row = int(image.shape[0] / 2)
    img_center_col = int(image.shape[1] / 2)

    upper_left = np.sum(image[:img_center_row,:img_center_col])
    upper_right = np.sum(image[:img_center_row,img_center_col:])
    bottom_right = np.sum(image[img_center_row:,img_center_col:])
    bottom_left = np.sum(image[img_center_row:,:img_center_col])
    
    array = np.array([upper_left, upper_right, bottom_right, bottom_left])
    return np.where(array==np.max(array))[0][0]

def shift_line(start, end, image, points=None):
    start = np.copy(start)
    end = np.copy(end)
    middle = midpoint(start, end)
    overlap1 = lineOverlap(start, middle, image)
    overlap2 = lineOverlap(middle, end, image)

    horizontal = False
    if np.abs(start[0]-end[0]) < np.abs(start[1]-end[1]):
        horizontal = True

    shift = -1
    if horizontal and start[0] < image.shape[0] / 2 and end[0] < image.shape[0] / 2:
        shift = +1
    elif not horizontal and start[1] < image.shape[1] / 2 and end[1] < image.shape[1] / 2:
        shift = +1

    if points is not None:
        if horizontal:
            start[0] += points*shift
            end[0] += points*shift
        else:
            start[1] += points*shift
            end[1] += points*shift
        return start, end
    
    shift_start = True
    counter = 0
    while (overlap1 + overlap2) / 2 < 0.9 and counter < max(image.shape):
        counter += 1
        if overlap1 < overlap2:
            if horizontal:
                start[0] += shift
            else: start[1] += shift

        elif overlap2 < overlap1:
            if horizontal:
                end[0] += shift
            else: end[1] += shift

        else:
            if shift_start:
                if horizontal: start[0] += shift
                else: start[1] += shift
                shift_start = not shift_start
            else:
                if horizontal: end[0] += shift
                else: end[1] += shift
                shift_start = not shift_start
        
        middle = midpoint(start, end)
        overlap1 = lineOverlap(start, middle, image)
        overlap2 = lineOverlap(middle, end, image)

    return start, end

def findTiming(image, coordinate1, coordinate2):
    overlap = lineOverlap(coordinate1, coordinate2, image)
    start, end = np.copy(coordinate1), np.copy(coordinate2)
    
    start, end = shift_line(start, end, image, image.shape[0]/2)
    while overlap > 0 and np.all(start > 0) and np.all(end > 0):
        start, end = shift_line(start, end, image, -12)
        overlap = lineOverlap(start, end, image)

    while overlap == 0:
        start, end = shift_line(start, end, image, 1)
        overlap = lineOverlap(start, end, image)

    best_start, best_end = None, None
    best_overlap = 0
    for i in range(30):
        start_, end_ = shift_line(start, end, image, i)
        overlap = lineOverlap(start_, end_, image)
        if overlap > best_overlap:
            best_start = start_
            best_end = end_
            best_overlap = overlap

    # due to the way circles are display (with flat sides), we shift the lines
    # to the center of the flat line
    best_start, best_end = shift_line(best_start, best_end, image, 4)
    return best_start, best_end

def numberofTransitions(dotimage, coordinate1, coordinate2):
    transitions = 0

    rr, cc = line(
        coordinate1[0], 
        coordinate1[1], 
        coordinate2[0], 
        coordinate2[1]
    )

    previousValue = False
    for r, c in zip(rr, cc):
        if dotimage[r, c] != previousValue:
            transitions += 1
            previousValue = dotimage[r, c]
    return transitions

def line_intersection(line1, line2):
    # see https://stackoverflow.com/a/20677983
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

def approximate_grid(coordinates, **kwargs):
    # create an image from the given coordinates to simulate a photo of an DMC
    image_ = create_image(coordinates)
    # connect dots with aperture size 30 (this should be adapted if the positions
    # are created with a different 'distance' value)
    module_size_approx = (np.max(coordinates[:,0]) - np.min(coordinates[:,1])) / 15
    image = connect_dots(image_, module_size_approx)

    labelled_image = label(image, connectivity=2)
    regions = regionprops(labelled_image)
    
    # choose the finder pattern from the connected components labelling
    # prefiltering using the criteria from Karrach and Pivarciova
    # final pattern is chosen based on the longest distance between the outer points
    finder_pattern = None
    for region in regions:

        size_criterium = region.area > 5000
        aspect = (region.bbox[2]-region.bbox[0]) / (region.bbox[3]-region.bbox[1])
        aspect_criterium = 0.5 <= aspect and aspect <= 2
        extent = region.area / region.area_bbox
        extent_criterium = 0.1 < extent < 0.6

        if size_criterium and aspect_criterium and extent_criterium:
            contour = Contour(region.coords)
            if finder_pattern == None or contour.longestDistance() > finder_pattern.longestDistance():
                finder_pattern = contour
              
    background = np.zeros_like(image)
    background[finder_pattern.coordinates[:,0], finder_pattern.coordinates[:,1]] = 1

    # the orientation is guessed based on the amount of pixels from the finder pattern
    # in each quarter of the image
    orientation = find_orientation(background)
    line1 = None
    line2 = None
    if orientation == 0:
        line1 = [[30, 30], [30, image.shape[1]-30]]
        line2 = [[30, 30], [image.shape[0]-30, 30]]

    elif orientation == 1:
        line1 = [[30, image.shape[1]-30], [30, 30]]
        line2 = [[30, image.shape[1]-30], [image.shape[0]-30, image.shape[1]-30]]

    elif orientation == 2:
        line1 = [[image.shape[0]-30, image.shape[1]-30], [image.shape[0]-30, 30]]
        line2 = [[image.shape[0]-30, image.shape[1]-30], [30, image.shape[1]-30]]

    elif orientation == 3:
        line1 = [[image.shape[0]-30, 30], [image.shape[0]-30, image.shape[1]-30]]
        line2 = [[image.shape[0]-30, 30], [30, 30]]

    line1 = shift_line(line1[0], line1[1], image)
    line2 = shift_line(line2[0], line2[1], image)

    line1 = shift_line(line1[0], line1[1], image, 11)
    line2 = shift_line(line2[0], line2[1], image, 11)
    
    line3 = findTiming(image, line1[0], line1[1])
    line4 = findTiming(image, line2[0], line2[1])

    # determine number of rows and columns
    transitions1 = numberofTransitions(image_, line3[0], line3[1])
    transitions2 = numberofTransitions(image_, line4[0], line4[1])

    l1l3 = np.abs(line1[0][0] - line3[0][0]) / (transitions1 - 1)
    l2l4 = np.abs(line2[0][1] - line4[0][1]) / (transitions2 - 1)
    
    grid = []
    # find row and column values
    for horizontal in range(transitions2):
        c1, c2 = shift_line(line2[0], line2[1], image, int(horizontal*l2l4))
        
        for vertical in range(transitions1):
            c3, c4 = shift_line(line1[0], line1[1], image, int(vertical*l1l3))
            grid.append(line_intersection([c1, c2], [c3, c4]))

    # we add 50 pixels to all coordinates at the beginning to avoid 
    # having 0 values and need to subract them here again.
    grid = np.asarray(grid) - 50
    return grid
