#!/usr/bin/python3

import time
from ev3.distance_detectors import EV3DistanceDetectors

if __name__ == "__main__":
    distance_detectors = EV3DistanceDetectors()
    distance_detectors.start()
    for _ in range(10):
        _distances = distance_detectors.get_distances()
        print('Distances = {}'.format(_distances))
        time.sleep(0.5)
    distance_detectors.stop()