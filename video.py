import numpy as np
import cv2 as cv
import mediapipe as mp
from PIL import Image
import math

# set up the mediapipe model globally so we don't recreate it on every frame
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=True,
                    min_detection_confidence=0.6, min_tracking_confidence=0.5)


def get_position(image_array):
    """
    Takes an image array (RGB format), runs MediaPipe pose detection,
    and returns the torso angle along with the position label.
    """
    results = pose.process(image_array)

    # Return early if no person is detected in the frame
    if not results.pose_landmarks:
        return None, "no_person_detected"

    # Extract shoulder and hip landmarks
    left_shoulder = results.pose_landmarks.landmark[11]
    right_shoulder = results.pose_landmarks.landmark[12]
    left_hip = results.pose_landmarks.landmark[23]
    right_hip = results.pose_landmarks.landmark[24]

    left_s_x = left_shoulder.x
    left_s_y = left_shoulder.y
    right_s_x = right_shoulder.x
    right_s_y = right_shoulder.y
    left_h_x = left_hip.x
    left_h_y = left_hip.y
    right_h_x = right_hip.x
    right_h_y = right_hip.y

    # Calculate midpoints for upper and lower torso
    x_shoulder_mid = (left_s_x + right_s_x) / 2.0
    y_shoulder_mid = (left_s_y + right_s_y) / 2.0

    x_hip_mid = (left_h_x + right_h_x) / 2.0
    y_hip_mid = (left_h_y + right_h_y) / 2.0

    # Calculate vector differences
    delta_x = x_shoulder_mid - x_hip_mid
    delta_y = y_shoulder_mid - y_hip_mid

    # Calculate angle in degrees
    angle_rad = math.atan2(delta_y, delta_x)
    angle_deg = math.degrees(angle_rad)
    angle_deg = abs(angle_deg)

    # Fold angles over 90 so range is strictly 0 to 90
    if angle_deg > 90:
        angle_deg = 180 - angle_deg

    # Determine position status based on thresholds
    if 0 <= angle_deg <= 34:
        status = "horizontal"
    elif 35 <= angle_deg <= 64:
        status = "bending / leaning"
    elif 65 <= angle_deg <= 90:
        status = "upright"
    else:
        status = "unknown"

    return angle_deg, status


# test image
image = Image.open("/Users/gill/Downloads/images.jpeg")
image_rgb = image.convert("RGB")
image_array = np.array(image_rgb)

angle, position = get_position(image_array)
print(f"Angle: {angle:.2f}°, Position: {position}")
