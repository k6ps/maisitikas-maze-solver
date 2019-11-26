#!/usr/bin/python3

import time
from ev3.motors import EV3Motors
from ev3.ultrasound_distance_detectors import EV3UltrasoundDistanceDetectors
from ev3.gyro import Gyro

if __name__ == "__main__":
    distance_sensors = EV3UltrasoundDistanceDetectors()
    distance_sensors.start()
    motors = EV3Motors(distance_sensors = distance_sensors, gyro = Gyro())
    for _ in range(5):
        motors.move_forward()
        time.sleep(1)
    distance_sensors.stop()
