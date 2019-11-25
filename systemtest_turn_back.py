#!/usr/bin/python3

import time
from ev3.motors import EV3Motors

if __name__ == "__main__":
    motors = EV3Motors()
    for _ in range(3):
        motors.turn_back()
        time.sleep(1)
