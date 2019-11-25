#!/usr/bin/python3

import time
from ev3.motors import EV3Motors

if __name__ == "__main__":
    motors = EV3Motors()
    for _ in range(12):
        motors.turn_right()
        time.sleep(1)
