import random

import cv2
import mediapipe as mp
import pyautogui
import util
from pynput.mouse import  Button, Controller


# Get screen dimensions
screen_width, screen_height = pyautogui.size()
mouse = Controller()

# Initialize Mediapipe Hands
mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=0,  # Lower complexity for faster tracking
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)

# Function to find the index finger tip position
def find_finger_tip(processed):
    if processed.multi_hand_landmarks:
        hand_landmarks = processed.multi_hand_landmarks[0]
        return hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
    return None

# Function to move the mouse pointer
def move_mouse(index_finger_tip):
    if index_finger_tip is not None:
        x = int(index_finger_tip.x * screen_width)
        y = int(index_finger_tip.y * screen_height)
        print(f"Moving mouse to: {x}, {y}")  # Debugging
        pyautogui.moveTo(x, y, duration=0.1)  # Small delay for smooth movement


def is_left_click(landmarks_list, thumb_index_dist):
    angle = util.get_angle(landmarks_list[5], landmarks_list[6], landmarks_list[8])
    return angle < 50 and thumb_index_dist > 250


def is_right_click(landmarks_list, thumb_index_dist):
    angle = util.get_angle(landmarks_list[9], landmarks_list[10], landmarks_list[12])
    return angle < 50 and thumb_index_dist > 250


def is_double_click(landmarks_list, thumb_index_dist):
    angle1 = util.get_angle(landmarks_list[5], landmarks_list[6], landmarks_list[8])
    angle2 = util.get_angle(landmarks_list[9], landmarks_list[10], landmarks_list[12])
    return angle1 < 70 and angle2 < 70 and thumb_index_dist < 300  # Adjusted thresholds

def is_screenshot(landmarks_list, thumb_index_dist):
    angle1 = util.get_angle(landmarks_list[5], landmarks_list[6], landmarks_list[8])
    angle2 = util.get_angle(landmarks_list[9], landmarks_list[10], landmarks_list[12])
    return angle1 < 70 and angle2 < 70 and thumb_index_dist < 100  # Adjusted thresholds
# Function to detect gestures
def detect_gestures(frame, landmarks_list, processed):
    if len(landmarks_list) >= 21:
        index_finger_tip = find_finger_tip(processed)
        thumb_index_dist = util.get_distance([landmarks_list[4], landmarks_list[8]])  # Thumb to index tip

        print(f"Thumb-Index Distance: {thumb_index_dist}")  # Debugging

        if thumb_index_dist < 250:  # Increased threshold
            print("✅ Gesture Detected: Moving Mouse")
            move_mouse(index_finger_tip)
        # LEFT CLICK
        elif is_left_click(landmarks_list,thumb_index_dist):
            mouse.press(Button.left)
            mouse.release(Button.left)
            cv2.putText(frame, "left click", (50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)


        # RIGHT CLICK
        elif is_right_click(landmarks_list, thumb_index_dist):
            mouse.press(Button.right)
            mouse.release(Button.right)
            cv2.putText(frame,"right click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        else:
            print("❌ Gesture Not Detected")

        # DOUBLE CLICK
        '''elif is_double_click(landmarks_list, thumb_index_dist):
            pyautogui.doubleClick()
            cv2.putText(frame, "double click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)'''



        # SCREENSHOT
        '''elif is_screenshot(landmarks_list, thumb_index_dist):
            im1 = pyautogui.screenshot()
            label = random.randint(1,1000)
            im1.save(f'my_screenshot_{label}.png')
            cv2.putText(frame, "screenshot taken", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)'''




# Main function
def main():
    cap = cv2.VideoCapture(0)  # Open webcam
    cap.set(3, 640)  # Set width
    cap.set(4, 480)  # Set height

    draw = mp.solutions.drawing_utils

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)  # Mirror effect
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            processed = hands.process(frameRGB)

            landmarks_list = []

            if processed.multi_hand_landmarks:
                hand_landmarks = processed.multi_hand_landmarks[0]
                draw.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS)

                for lm in hand_landmarks.landmark:
                    landmarks_list.append([lm.x, lm.y])  # Append normalized coordinates

            detect_gestures(frame, landmarks_list, processed)

            cv2.imshow('Virtual Mouse', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()