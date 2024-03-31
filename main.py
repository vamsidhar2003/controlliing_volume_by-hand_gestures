import cv2
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np

def set_volume_level(volume_level):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # Retrieve the current volume range
    volume_range = volume.GetVolumeRange()

    # Calculate the volume level to set within the volume range
    new_volume = (volume_range[1] - volume_range[0]) * volume_level + volume_range[0]

    # Set the volume
    volume.SetMasterVolumeLevel(new_volume, None)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)
with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                lm = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)

                cv2.circle(image, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

                # Adjust volume based on hand position
                volume_level = np.interp(cy, [50, h - 50], [0, 1])
                set_volume_level(volume_level)

        cv2.imshow('Hand Gesture Volume Control', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
