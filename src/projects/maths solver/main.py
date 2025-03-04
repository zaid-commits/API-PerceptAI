import cvzone
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import google.generativeai as genai
from PIL import Image
import time

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)
detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.7, minTrackCon=0.5)

genai.configure(api_key="AIzaSyAvFuzunIKLW7t2nVTX51DsswnzW3UyE0w")  # Update with your API key
model = genai.GenerativeModel('gemini-1.5-flash')

# Cooldown management
last_request_time = 0
request_cooldown = 60  # 60 seconds cooldown between requests

# Function to detect hand gestures
def getHandInfo(img):
    hands, img = detector.findHands(img, draw=True, flipType=True)
    if hands:
        hand = hands[0]  # Get the first hand detected
        lmList = hand["lmList"]
        fingers = detector.fingersUp(hand)
        return fingers, lmList
    else:
        return None

# Function to draw on the canvas
def draw(info, prev_pos, canvas):
    fingers, lmList = info
    current_pos = None
    if fingers == [0, 1, 0, 0, 0]:  # Index finger up for drawing
        current_pos = lmList[8][0:2]  # Index finger tip position
        if prev_pos is None: prev_pos = current_pos
        cv2.line(canvas, current_pos, prev_pos, (255, 0, 255), 10)
    elif fingers == [1, 0, 0, 0, 0]:  # Fist gesture to clear the canvas
        canvas = np.zeros_like(img)
    return current_pos, canvas

# Function to send canvas to the AI model
def sendToAI(model, canvas, fingers):
    global last_request_time
    current_time = time.time()

    if current_time - last_request_time > request_cooldown:
        if fingers == [0, 0, 1, 1, 1]:  # Triggered when middle, ring, and pinky fingers are raised
            pil_image = Image.fromarray(canvas)
            response = model.generate_content(["Solve this math problem", pil_image])
            last_request_time = current_time  # Update the last request time
            return response.text
    else:
        return None  # If cooldown period hasn't passed, return None

# Function to overlay the answer on the GUI window
def draw_answer_on_screen(img, answer):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = "Answer: " + answer
    cv2.putText(img, text, (50, 50), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
    return img

# Main loop for capturing webcam feed and processing
prev_pos = None
canvas = None
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)  # Flip the image for mirror effect

    if canvas is None:
        canvas = np.zeros_like(img)

    info = getHandInfo(img)
    if info:
        fingers, lmList = info
        prev_pos, canvas = draw(info, prev_pos, canvas)
        answer = sendToAI(model, canvas, fingers)  # Get AI response

        if answer:
            img = draw_answer_on_screen(img, answer)  # Overlay answer on the frame

    image_combined = cv2.addWeighted(img, 0.7, canvas, 0.3, 0)
    cv2.imshow("Image", image_combined)
    cv2.waitKey(1)
