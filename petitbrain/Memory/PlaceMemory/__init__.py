import numpy as np

MIN_PLACE_CELL_DISTANCE = 200  # 100
ICP_DISTANCE_THRESHOLD = 300
ANGULAR_RESOLUTION = 1  # Degree
CONE_HALF_ANGLE = 20  # 25

# Arrays to compute the echo curve
MASK_ARRAY = np.zeros(360 // ANGULAR_RESOLUTION, dtype=float)
MASK_ARRAY[:CONE_HALF_ANGLE // ANGULAR_RESOLUTION] = 1
MASK_ARRAY[-CONE_HALF_ANGLE // ANGULAR_RESOLUTION:] = 1
