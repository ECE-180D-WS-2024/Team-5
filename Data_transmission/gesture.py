import mediapipe as mp
import numpy as np
import xgboost as xgb

# To decode gesture prediction
gesture_map = {0:"Block", 1:"Idle", 2:"Kick", 3:"Punch"}

# Load the model from a file
xgb_clf = xgb.XGBClassifier()
xgb_clf.load_model('xgb_model_v2.json')

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

# Primary function to get gesture predictions
def get_gesture(landmarks, classifier=xgb_clf):
    data = preprocess_landmarks(landmarks)
    return gesture_map[classifier.predict(data)[0]]