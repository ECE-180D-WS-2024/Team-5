import cv2

# Initialize the webcam (0 is the default camera)
cap = cv2.VideoCapture(1)

# Define the codec and create VideoWriter object (will be initialized later)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = None

is_recording = False

def reduce_glare(frame):
    # Convert the image to LAB color space
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    
    # Split the LAB image into different channels
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to the L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    # Merge the CLAHE enhanced L channel back with A and B channels
    limg = cv2.merge((cl, a, b))
    
    # Convert the LAB image back to BGR format
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return final

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    
    frame_height, frame_width = frame.shape[:2]

    # Reduce glare in the frame
    # frame = reduce_glare(frame)

    # Display the resulting frame
    cv2.imshow('Webcam Video', frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('r'):
        if not is_recording:
            is_recording = True
            # Initialize the VideoWriter object
            out = cv2.VideoWriter('boelter_ryan.avi', fourcc, 20.0, (frame_width, frame_height))
            print("Recording started...")
        else:
            print("Already recording...")

    if is_recording:
        out.write(frame)

    if key == ord('q'):
        if is_recording:
            is_recording = False
            out.release()
            print("Recording stopped and saved.")
        break

# Release the capture and writer objects and close the window
cap.release()
if out is not None:
    out.release()
cv2.destroyAllWindows()