#!/usr/bin/python3

import time
from ev3.ultrasound_distance_detectors import EV3UltrasoundDistanceDetectors

if __name__ == "__main__":
    distance_detectors = EV3UltrasoundDistanceDetectors()
    distance_detectors.start()
    for _ in range(10):
        _distances = distance_detectors.get_distances()
        print('Distances = {}'.format(_distances))
        time.sleep(0.5)
    distance_detectors.stop()