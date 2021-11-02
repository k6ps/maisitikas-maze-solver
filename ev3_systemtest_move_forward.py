#!/usr/bin/python3

import time
from ev3.motors import EV3Motors
from ev3.distance_detectors import EV3DistanceDetectors
from ev3.gyro import Gyro

if __name__ == "__main__":
    distance_sensors = EV3DistanceDetectors()
    distance_sensors.start()
    motors = EV3Motors(distance_sensors = distance_sensors, gyro = Gyro())
    for _ in range(5):
        motors.move_forward()
        time.sleep(1)
    distance_sensors.stop()
