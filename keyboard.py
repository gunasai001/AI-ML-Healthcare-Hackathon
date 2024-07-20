import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import cvzone
from pynput.keyboard import Controller


class Button:
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.size = size
        self.text = text


class VirtualKeyboard:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

        self.detector = HandDetector(detectionCon=0.8, maxHands=1)

        self.keys = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
            ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]
        ]

        self.buttonList = self.init_buttons()

        self.finalText = ""
        self.keyboard = Controller()


        self.clicked = False
        self.click_cooldown = 0

    def init_buttons(self):
        buttons = []
        for i, row in enumerate(self.keys):
            for j, key in enumerate(row):
                buttons.append(Button([100 * j + 50, 100 * i + 50], key))
        return buttons

    def draw_all(self, img):
        for button in self.buttonList:
            x, y = button.pos
            w, h = button.size
            cvzone.cornerRect(img, (x, y, w, h), 20, rt=0)
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), cv2.FILLED)
            cv2.putText(img, button.text, (x + 20, y + 65),
                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
        return img

    def draw_text_box(self, img):
        cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
        cv2.putText(img, self.finalText, (60, 430),
                    cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    def handle_click(self, l, button):
        if l < 30 and not self.clicked and self.click_cooldown == 0:
            self.keyboard.press(button.text)
            self.finalText += button.text
            self.clicked = True
            self.click_cooldown = 10  # Set cooldown to prevent multiple clicks

    def run(self):
        while True:
            success, img = self.cap.read()
            img = cv2.flip(img, 1)  # Mirror the image
            hands, img = self.detector.findHands(img, flipType=False)

            img = self.draw_all(img)
            self.draw_text_box(img)

            if hands:
                hand = hands[0]
                lmList = hand["lmList"]
                for button in self.buttonList:
                    x, y = button.pos
                    w, h = button.size
                    if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                        cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                        cv2.putText(img, button.text, (x + 20, y + 65),
                                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                        distance_info = self.detector.findDistance(lmList[8][:2], lmList[12][:2])
                        if distance_info:
                            l = distance_info[0]
                            self.handle_click(l, button)

            # Reset click state if fingers are far apart
            if not hands or (hands and self.detector.findDistance(lmList[8][:2], lmList[12][:2])[0] > 50):
                self.clicked = False

            # Decrement cooldown
            if self.click_cooldown > 0:
                self.click_cooldown -= 1

            cv2.imshow("Virtual Keyboard", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    keyboard = VirtualKeyboard()
    keyboard.run()