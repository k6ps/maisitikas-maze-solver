import time
import logging
from ev3.simple_worker_thread import SimplePeriodicWorkerThread
from ev3dev2.sensor.lego import UltrasonicSensor

class EV3UltrasoundDistanceDetectors(SimplePeriodicWorkerThread):

    def __init__(self, logger = None):
        self._logger = logger or logging.getLogger(__name__)
        super().__init__(thread_name = 'EV3UltrasoundDistanceDetectors')
        self._sensor_left = UltrasonicSensor(address='in4')
        self._sensor_front = UltrasonicSensor(address='in3')
        self._sensor_right = UltrasonicSensor(address='in2')
        self._distance_left = 255.0
        self._distance_front = 255.0
        self._distance_right = 255.0
        self._last_distances_queue_left = []
        self._last_distances_queue_right = []
        self._LAST_DISTANCES_QUEUE_MAX_LENGTH = 25

    def _add_distance_to_queue(self, queue: list, distance: float):
        queue.append(distance)
        if len(queue) > self._LAST_DISTANCES_QUEUE_MAX_LENGTH:
            queue.pop(0)

    def perform_cycle(self):
        self._distance_left = round(self._sensor_left.distance_centimeters, 1)
        self._distance_front = round(self._sensor_front.distance_centimeters, 1)
        self._distance_right = round(self._sensor_right.distance_centimeters, 1)
        self._logger.debug('left={}, front={}, right={}'.format(
            self._distance_left, 
            self._distance_front, 
            self._distance_right
        ))
        self._add_distance_to_queue(self._last_distances_queue_left, self._distance_left)
        self._add_distance_to_queue(self._last_distances_queue_right, self._distance_right)

    def get_distances(self):
        # It is ok to read slightly outdated data
        return {
            'left': self._distance_left,
            'front': self._distance_front,
            'right': self._distance_right
        }
