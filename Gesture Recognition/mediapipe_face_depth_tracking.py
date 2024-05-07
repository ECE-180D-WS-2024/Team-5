import cv2
import mediapipe as mp

mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(static_image_mode=False, model_complexity=1, enable_segmentation=True)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = holistic.process(image)

    if results.pose_landmarks:
        # Use multiple 3D landmarks to estimate depth
        landmarks = results.pose_landmarks.landmark
        nose = landmarks[mp_holistic.PoseLandmark.NOSE]
        left_eye = landmarks[mp_holistic.PoseLandmark.LEFT_EYE_INNER]
        right_eye = landmarks[mp_holistic.PoseLandmark.RIGHT_EYE_INNER]

        # Example: Average depth (z-coordinate)
        average_depth = (nose.z + left_eye.z + right_eye.z) / 3
        print("Average Depth:", average_depth)

    cv2.imshow('MediaPipe Holistic', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()