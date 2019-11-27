#!/usr/bin/python3

import time
import logging
import sys
from ev3.motors import EV3Motors
from ev3.ultrasound_distance_detectors import EV3UltrasoundDistanceDetectors
from ev3.gyro import Gyro


def set_up_console_logging():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.basicConfig(level=logging.INFO, handlers=[console_handler])
    logging.getLogger('ev3.motors').setLevel(logging.DEBUG)

if __name__ == "__main__":
    set_up_console_logging()
    distance_sensors = EV3UltrasoundDistanceDetectors()
    gyro = Gyro()
    motors = EV3Motors(distance_sensors = distance_sensors, gyro = gyro)
    distance_sensors.start()
    gyro.start()
    for _ in range(12):
        motors.turn_right()
        time.sleep(1)
    distance_sensors.stop()
    gyro.stop()
