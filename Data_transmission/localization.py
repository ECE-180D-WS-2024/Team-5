import mediapipe as mp

# Mediapipe setup
mp_pose = mp.solutions.pose

# TODO: Determine thresholds dynamically based on player height
forward_threshold = 0.7
backward_theshold = 0.55

# Calculate player height using heel and nose
def get_player_height(landmarks):
    nose = landmarks[0]
    left_heel = landmarks[29]
    right_heel = landmarks[30]

    # Ensure visibility of critical points
    if nose.visibility < 0.6 or left_heel.visibility < 0.6\
        or right_heel.visibility < 0.6:
        return None, "Player not fully visible."

    # Get the lowermost heel
    foot_y = max(left_heel.y, right_heel.y)

    # Calculate fractional height
    player_height = abs(nose.y - foot_y)
    return player_height, None

# Get relative player movement based on height
def get_player_movement(results):
    player_height, error_message = get_player_height(results)
    if error_message:
        print(f"Error: ", error_message)
        return "MoveError"
    # Determine movement command based on height
    if player_height > forward_threshold:
        return "MoveForward"
    if player_height < backward_theshold:
        return "MoveBackward"
    return "MoveStill"