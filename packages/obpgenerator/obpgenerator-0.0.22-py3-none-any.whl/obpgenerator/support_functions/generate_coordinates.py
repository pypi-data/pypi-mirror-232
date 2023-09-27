import math
import numpy as np

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in degree.
    """
    angle = math.radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

def rotate_matrix(matrix, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in degree.
    """

    # convert the angle to radians
    angle_rad = np.radians(angle)

    # separate the array into x and y coordinates
    x = matrix.real
    y = matrix.imag

    # apply the rotation
    x_new = x * np.cos(angle_rad) - y * np.sin(angle_rad)
    y_new = x * np.sin(angle_rad) + y * np.cos(angle_rad)

    # combine the new x and y coordinates back into complex numbers
    arr_rotated = x_new + 1j * y_new
    return arr_rotated

def generate_matrices(spacing, size=150, angle=0): #spacing and size in mm, angle in degree 
    row_height = math.sqrt(3/4)*spacing
    points_x = math.floor(size/spacing)
    points_y = math.floor(size/row_height)
    
    coord_matrix = np.zeros((points_y, points_x), dtype=np.complex_)
    keep_matrix = np.zeros((points_y, points_x))

    # Generate ranges for x and y
    x_range = np.arange(points_x) * spacing - size / 2
    y_range = np.arange(points_y) * row_height - size / 2

    # Reshape to make broadcasting work
    x_range = x_range.reshape((1, -1))
    y_range = y_range.reshape((-1, 1))

    # Generate x and y values for all points
    x_values = x_range
    y_values = y_range

    # Combine x and y values into complex coordinates
    coord_matrix = x_values + 1j * y_values
    coord_matrix[1::2] += spacing/2

    if angle != 0:
        # If angle != 0, apply rotation to all points at once
        coord_matrix = rotate_matrix(coord_matrix, angle)

    return coord_matrix, keep_matrix