import numpy as np
import cv2
import random
import mediapipe as mp
import time  # Import time module

# Initialize game window
width, height = 640, 480
window = np.zeros((height, width, 3), dtype=np.uint8)

# Snake settings
snake_pos = [(100, 50), (90, 50), (80, 50)]
snake_direction = 'RIGHT'
change_to = snake_direction

# Food settings
food_pos = [random.randrange(1, (width // 10)) * 10, random.randrange(1, (height // 10)) * 10]
food_spawn = True

# Game settings
score = 0
speed = 15

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Function to detect hand gestures
def detect_gesture(hand_landmarks):
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    # Check if index finger is pointing up
    if index_tip.y < middle_tip.y and index_tip.y < wrist.y:
        if abs(index_tip.x - wrist.x) < abs(index_tip.y - wrist.y):
            return "UP"
        elif index_tip.x < wrist.x:
            return "LEFT"
        elif index_tip.x > wrist.x:
            return "RIGHT"

    # Check if index finger is pointing down
    if index_tip.y > middle_tip.y and index_tip.y > wrist.y:
        if abs(index_tip.x - wrist.x) < abs(index_tip.y - wrist.y):
            return "DOWN"

    # Check if hand is closed (fist)
    if thumb_tip.y > index_tip.y and thumb_tip.y > middle_tip.y:
        return "FIST"

    return "NONE"

# Main game loop
game_over = False
while not game_over:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture = detect_gesture(hand_landmarks)

            if gesture == "LEFT" and snake_direction != 'RIGHT':
                change_to = 'LEFT'
            elif gesture == "RIGHT" and snake_direction != 'LEFT':
                change_to = 'RIGHT'
            elif gesture == "UP" and snake_direction != 'DOWN':
                change_to = 'UP'
            elif gesture == "DOWN" and snake_direction != 'UP':
                change_to = 'DOWN'

    # Update snake direction
    snake_direction = change_to

    # Update snake position
    head_x, head_y = snake_pos[0]
    if snake_direction == 'UP':
        head_y -= 10
    elif snake_direction == 'DOWN':
        head_y += 10
    elif snake_direction == 'LEFT':
        head_x -= 10
    elif snake_direction == 'RIGHT':
        head_x += 10
    new_head = (head_x, head_y)

    # Snake body growing mechanism
    snake_pos.insert(0, new_head)
    if snake_pos[0] == tuple(food_pos):
        score += 1
        food_spawn = False
    else:
        snake_pos.pop()

    if not food_spawn:
        food_pos = [random.randrange(1, (width // 10)) * 10, random.randrange(1, (height // 10)) * 10]
    food_spawn = True

    # Fill window with black color
    window[:] = (0, 0, 0)

    # Draw snake
    for pos in snake_pos:
        cv2.rectangle(window, pos, (pos[0] + 10, pos[1] + 10), (0, 255, 0), -1)

    # Draw food
    cv2.rectangle(window, tuple(food_pos), (food_pos[0] + 10, food_pos[1] + 10), (0, 0, 255), -1)

    # Game Over conditions
    if snake_pos[0][0] < 0 or snake_pos[0][0] >= width or snake_pos[0][1] < 0 or snake_pos[0][1] >= height:
        game_over = True
    for block in snake_pos[1:]:
        if snake_pos[0] == block:
            game_over = True

    # Display the game window
    cv2.imshow('Snake Game', window)
    cv2.imshow('Hand Gesture', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.2)  # Add delay to reduce the speed of the snake

cap.release()
cv2.destroyAllWindows()