import time
import pyautogui
import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

cap = cv2.VideoCapture(0)

screen_width, screen_height = pyautogui.size()

buffer = 50

def count_fingers(hand_landmarks):
    cnt = 0
    thresh = (hand_landmarks.landmark[0].y * 100 - hand_landmarks.landmark[9].y * 100) / 2

    if (hand_landmarks.landmark[5].y * 100 - hand_landmarks.landmark[8].y * 100) > thresh:
        cnt += 1
    if (hand_landmarks.landmark[9].y * 100 - hand_landmarks.landmark[12].y * 100) > thresh:
        cnt += 1
    if (hand_landmarks.landmark[13].y * 100 - hand_landmarks.landmark[16].y * 100) > thresh:
        cnt += 1
    if (hand_landmarks.landmark[17].y * 100 - hand_landmarks.landmark[20].y * 100) > thresh:
        cnt += 1
    if (hand_landmarks.landmark[5].x * 100 - hand_landmarks.landmark[4].x * 100) > 6:
        cnt += 1

    return cnt
def get_gesture_and_position(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        finger_count = count_fingers(hand_landmarks)
        
        x = hand_landmarks.landmark[8].x
        y = hand_landmarks.landmark[8].y
        
        return finger_count, (x, y)
    
    return None, None

def map_to_screen(hand_pos):
    x = np.interp(hand_pos[0], [0, 1], [-buffer, screen_width + buffer])
    y = np.interp(hand_pos[1], [0, 1], [-buffer, screen_height + buffer])
    
    x = max(0, min(x, screen_width))
    y = max(0, min(y, screen_height))
    
    return int(x), int(y)

last_y = None
scroll_speed = 2
scroll_threshold = 0.001  

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    gesture, hand_pos = get_gesture_and_position(frame)

    if gesture is not None and hand_pos is not None:
        if gesture == 1: 
            x, y = map_to_screen(hand_pos)
            pyautogui.moveTo(x, y)
        elif gesture == 2:
            pyautogui.click()
            time.sleep(0.1)
        elif gesture == 3: 
            pyautogui.rightClick()
            time.sleep(0.1)
        elif gesture == 4: 
            pyautogui.doubleClick()
            time.sleep(0.1)
        elif gesture == 5: 
            if last_y is not None:
                y_diff = hand_pos[1] - last_y
                if abs(y_diff) > scroll_threshold:
                    scroll_amount = int(y_diff * scroll_speed * screen_height)
                    pyautogui.scroll(-scroll_amount)
            last_y = hand_pos[1]
    else:
        last_y = None

    cv2.imshow('Gesture Control', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()