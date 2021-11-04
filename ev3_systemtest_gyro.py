#!/usr/bin/python3

import time
from ev3.gyro import Gyro

if __name__ == "__main__":
    gyro = Gyro()
    gyro.start()
    for _ in range(10):
        _angle = gyro.get_orientation()
        print('Angle = {}'.format(_angle))
        time.sleep(1)
    gyro.stop()
