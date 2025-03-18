import numpy as np

# Function to calculate the angle between three points
def get_angle(a, b, c):
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(np.degrees(radians))
    return angle

# Function to calculate Euclidean distance between two landmarks
def get_distance(landmark_list):
    if len(landmark_list) < 2:
        return 0  # Return 0 instead of None to avoid errors

    (x1, y1), (x2, y2) = landmark_list[0], landmark_list[1]

    # Convert normalized coordinates (0-1) to screen coordinates
    x1, y1 = int(x1 * 1920), int(y1 * 1080)  # Assuming Full HD screen resolution
    x2, y2 = int(x2 * 1920), int(y2 * 1080)

    # Compute Euclidean distance
    return np.hypot(x2 - x1, y2 - y1)










'''import numpy as np

def get_angle(a,b,c):
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(np.degrees(radians))
    return angle

def get_distance(landmark_list):
    if len(landmark_list)<2:
        return
    (x1,y1), (x2,y2) = landmark_list[0], landmark_list[1]
    L = np.hypot(x2-x1, y2-y1)
    return np.interp(L, [0,1], [0,1000])'''