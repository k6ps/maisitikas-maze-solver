#!/usr/bin/python3

import time
from ev3.motors import EV3Motors

if __name__ == "__main__":
    motors = EV3Motors()
    motors.turn_left()
    time.sleep(1)
    motors.turn_right()
    time.sleep(1)
    motors.turn_left()
    time.sleep(1)
    motors.turn_back()
    time.sleep(1)
    motors.turn_right()
    time.sleep(1)
    motors.turn_left()
    time.sleep(1)
    motors.turn_right()
    time.sleep(1)
    motors.turn_back()
