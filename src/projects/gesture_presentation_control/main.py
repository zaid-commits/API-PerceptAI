import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Gesture states
prev_hand_state = None
last_gesture_time = 0
gesture_cooldown = 1  # 1 second cooldown between gestures

def detect_gesture(hand_landmarks):
    # Get landmark positions
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    
    # Check if index finger is pointing (extended)
    if index_tip.y < middle_tip.y and index_tip.y < wrist.y:
        if index_tip.x < wrist.x:
            return "LEFT"
        elif index_tip.x > wrist.x:
            return "RIGHT"
    
    # Check if hand is closed (fist)
    if thumb_tip.y > index_tip.y and thumb_tip.y > middle_tip.y:
        return "FIST"
    
    return "NONE"

print("Starting gesture recognition. Press 'q' to quit.")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Failed to capture frame. Skipping...")
        continue

    # Flip the image horizontally for a later selfie-view display
    image = cv2.flip(image, 1)
    
    # Convert the BGR image to RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Process the image and detect hands
    results = hands.process(rgb_image)

    current_time = time.time()
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw hand landmarks
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Detect gesture
            gesture = detect_gesture(hand_landmarks)
            
            # Display gesture on the image
            cv2.putText(image, f"Gesture: {gesture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            if gesture != prev_hand_state and current_time - last_gesture_time > gesture_cooldown:
                if gesture == "LEFT":
                    print("Detected LEFT gesture. Simulating left arrow key press.")
                    pyautogui.press('left')
                    last_gesture_time = current_time
                elif gesture == "RIGHT":
                    print("Detected RIGHT gesture. Simulating right arrow key press.")
                    pyautogui.press('right')
                    last_gesture_time = current_time
                elif gesture == "FIST":
                    print("Detected FIST gesture. Simulating F5 key press.")
                    pyautogui.press('f5')
                    last_gesture_time = current_time
                
                prev_hand_state = gesture

    cv2.imshow('Gesture Presentation Control', image)
    if cv2.waitKey(5) & 0xFF == ord('q'):  # Press 'q' to exit
        break

cap.release()
cv2.destroyAllWindows()
print("Gesture recognition stopped.")
