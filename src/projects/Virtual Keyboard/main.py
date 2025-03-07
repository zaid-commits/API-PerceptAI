import cv2
import numpy as np
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Define the keyboard layout
keys = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
]

# Variable to store typed text
typed_text = ""

# Function to draw the keyboard
def draw_keyboard(img):
    key_width = 60
    key_height = 60
    start_x = 50
    start_y = 50
    for i, row in enumerate(keys):
        for j, key in enumerate(row):
            x = start_x + j * key_width
            y = start_y + i * key_height
            cv2.rectangle(img, (x, y), (x + key_width, y + key_height), (255, 0, 0), 2)
            cv2.putText(img, key, (x + 20, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

# Function to detect key press
def detect_key_press(hand_landmarks, img):
    key_width = 60
    key_height = 60
    start_x = 50
    start_y = 50
    for i, row in enumerate(keys):
        for j, key in enumerate(row):
            x = start_x + j * key_width
            y = start_y + i * key_height
            for lm in hand_landmarks.landmark:
                cx, cy = int(lm.x * img.shape[1]), int(lm.y * img.shape[0])
                if x < cx < x + key_width and y < cy < y + key_height:
                    cv2.rectangle(img, (x, y), (x + key_width, y + key_height), (0, 255, 0), 2)
                    cv2.putText(img, key, (x + 20, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    return key
    return None

# Function to draw typed text
def draw_text(img, text):
    cv2.putText(img, text, (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

# Initialize webcam
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            key = detect_key_press(hand_landmarks, img)
            if key:
                typed_text += key
                print(f"Key Pressed: {key}")

    draw_keyboard(img)
    draw_text(img, typed_text)
    cv2.imshow("Virtual Keyboard", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()