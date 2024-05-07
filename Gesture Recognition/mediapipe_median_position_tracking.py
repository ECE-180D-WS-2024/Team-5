import cv2
import mediapipe as mp
import time
import numpy as np

# Initialize MediaPipe Pose and drawing utilities
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

def remove_outliers(data):
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return [x for x in data if lower_bound <= x <= upper_bound]

# Start capturing video
cap = cv2.VideoCapture(0)

# Landmark indices
LEFT_SHOULDER_INDEX = mp_pose.PoseLandmark.LEFT_SHOULDER.value
RIGHT_SHOULDER_INDEX = mp_pose.PoseLandmark.RIGHT_SHOULDER.value

# Initialize an array to store z-positions and start time
z_positions = []
start_time = time.time()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # frame = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_LINEAR)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        # mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        landmarks = results.pose_landmarks.landmark
        z_pos = 0
        count = 0

        for idx in [LEFT_SHOULDER_INDEX, RIGHT_SHOULDER_INDEX]:
            landmark = landmarks[idx]
            if landmark.visibility > 0.8:
                z_pos += landmark.z
                count += 1

        # if landmarks[LEFT_SHOULDER_INDEX].visibility > 0.8:
        #    z_positions.append(landmarks[LEFT_SHOULDER_INDEX].z)

        if count == 2:
            z_positions.append(z_pos / count)

        # Example usage within your capture loop
        if time.time() - start_time >= 1:
            if z_positions:
                filtered_positions = remove_outliers(z_positions)
                if filtered_positions:  # Check if list is not empty after removing outliers
                    final_z_position = np.median(filtered_positions)
                    print(f"Filtered Datapoints captured: {len(filtered_positions)}")
                    print(f"Median z position over the last half second (outliers removed): {final_z_position * (-10):.4f}")
                else:
                    print("All data points were considered outliers.")
            z_positions = []
            start_time = time.time()

cap.release()