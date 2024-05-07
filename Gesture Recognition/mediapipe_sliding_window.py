import cv2
import mediapipe as mp
import time
import numpy as np
from collections import deque

# Initialize MediaPipe Pose and drawing utilities
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

upper_bound = lower_bound = 0

def remove_outliers(data):
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return [x for x in data if lower_bound <= x <= upper_bound], upper_bound, lower_bound

# Start capturing video
cap = cv2.VideoCapture(0)

# Landmark indices
LEFT_SHOULDER_INDEX = mp_pose.PoseLandmark.LEFT_SHOULDER.value
RIGHT_SHOULDER_INDEX = mp_pose.PoseLandmark.RIGHT_SHOULDER.value

# Initialize a deque to store z-positions and start time
z_positions = deque(maxlen=100)
start_time = time.time()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        z_pos = 0
        count = 0

        for idx in [LEFT_SHOULDER_INDEX, RIGHT_SHOULDER_INDEX]:
            landmark = landmarks[idx]
            if landmark.visibility > 0.8:
                z_pos += landmark.z
                count += 1

        if count == 2:
            current_z_pos = z_pos / count
            if len(z_positions) < 100 or (lower_bound <= current_z_pos <= upper_bound):  # First add or check if not an outlier
                z_positions.append(current_z_pos)

        if len(z_positions) == 100 and time.time() - start_time >= 0.5:
            if z_positions:
                filtered_positions, upper_bound, lower_bound = remove_outliers(z_positions)
                if filtered_positions:
                    final_z_position = np.median(filtered_positions)
                    print(f"Filtered Datapoints captured: {len(filtered_positions)}")
                    print(f"Median z position over the last half second (outliers removed): {final_z_position * (-10):.4f}")
                else:
                    print("All data points were considered outliers.")
            start_time = time.time()

cap.release()
