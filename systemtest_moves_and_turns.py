#!/usr/bin/python3

import time
from ev3.motors import EV3Motors

if __name__ == "__main__":
    motors = EV3Motors()
    motors.move_forward()
    motors.turn_left()
    motors.move_forward()
    motors.turn_right()
    motors.move_forward()
    motors.turn_right()
    motors.move_forward()
    motors.turn_left()
    motors.move_forward()
    motors.turn_right()
    motors.move_forward()
    motors.turn_right()
    motors.move_forward()
    motors.turn_left()
    motors.move_forward()
    motors.turn_right()
    motors.move_forward()
    motors.turn_right()
    motors.move_forward()
    motors.turn_left()
    motors.move_forward()
    motors.turn_right()
    motors.move_forward()
    motors.turn_right()
