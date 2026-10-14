from collections import deque
from time import time
from video import get_position
history = deque(maxlen=15)
current_state = "NORMAL"
stillness_start_time = None

while camera_is_running:
    frame = get_frame()
    current_time = time.time()

    # get info about current pose
    angle, position = get_position(frame)
    if position == "no_person_detected":
        continue

    history.append((angle, position, current_time))

    # calculate the oldest frame in history to get speed of drop
    oldest_angle, oldest_position, oldest_time = history[0]
    angle_change = oldest_angle - angle

    # State Machine
    if current_state == "NORMAL":
        if angle_change > 45 and position == "horizontal":
            current_state = "SUSPECTED_FALL"
            stillness_start_time = current_time
    elif current_state == "SUSPECTED_FALL":
        if position == "upright":
            current_state = "NORMAL"
            stillness_start_time = None
        elif position == "horizontal":
            if (current_time - stillness_start_time) >= 3.0:
                current_state = "BUZZING"
    elif current_state == "BUZZING":
        # ALARM LOGIC PHASE 4
        pass
