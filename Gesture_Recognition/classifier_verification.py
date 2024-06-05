import cv2
import mediapipe as mp
import xgboost as xgb
import numpy as np

# Initialize MediaPipe pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.8, min_tracking_confidence=0.8)

# Load the model from a file
xgb_clf = xgb.XGBClassifier()
xgb_clf.load_model('xgb_model_v1.json')

gesture_map = {0:"Block", 1:"Idle", 2:"Kick", 3:"Punch"}

# Function to preprocess landmarks for prediction
def preprocess_landmarks(landmarks):
    # Extract x and y coordinates
    x_coords = np.array([landmark.x for landmark in landmarks])
    y_coords = np.array([landmark.y for landmark in landmarks])
    visibility = np.array([landmark.visibility for landmark in landmarks])
    
    # Center the landmarks
    x_center = (x_coords.min() + x_coords.max()) / 2
    y_center = (y_coords.min() + y_coords.max()) / 2
    x_coords -= x_center
    y_coords -= y_center
    
    # Stack and reshape the coordinates to interleave them
    stacked_coords = np.stack((x_coords, y_coords, visibility), axis=-1)
    data = stacked_coords.reshape(-1)
    return data

# Open the video file
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Get frame dimensions
    height, width, _ = frame.shape
    
    # Calculate the width to be half of the height
    new_width = height // 2
    start_x = (width - new_width) // 2
    end_x = start_x + new_width
    
    # Crop the frame to the calculated dimensions
    image = frame[:, start_x:end_x]
    
    # Convert the frame to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    
    # Process the image to extract pose landmarks
    results = pose.process(image)
    
    # Convert back to BGR for rendering
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    if results.pose_landmarks:
        # Extract and preprocess landmarks
        landmarks = results.pose_landmarks.landmark
        data = preprocess_landmarks(landmarks).reshape(1, -1)

        # Make prediction
        prediction = gesture_map[xgb_clf.predict(data)[0]]

        # Block: 0, Idle: 1, Kick: 2, Punch: 3

        # Draw landmarks on the frame
        mp.solutions.drawing_utils.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Display predicted class on the frame
        cv2.putText(image, f'Prediction: {prediction}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    
    # Display the image
    cv2.imshow('Frame', image)
    
    if cv2.waitKey(5) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()