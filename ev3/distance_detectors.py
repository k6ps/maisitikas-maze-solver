import time
import math
import logging
from ev3.simple_worker_thread import SimplePeriodicWorkerThread
from ev3dev2.sensor.lego import ColorSensor

class EV3DistanceDetectors(SimplePeriodicWorkerThread):

    def __init__(self, logger = None):
        self._logger = logger or logging.getLogger(__name__)
        super().__init__(thread_name = 'EV3DistanceDetectors')
        self._sensor_left = LightDistanceSensor(address='in3')
        self._sensor_front = LightDistanceSensor(address='in1')
        self._sensor_right = LightDistanceSensor(address='in4')
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
        self._distance_left = self._sensor_left.distance_centimeters()
        self._distance_front = self._sensor_front.distance_centimeters()
        self._distance_right = self._sensor_right.distance_centimeters()
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


class LightDistanceSensor(object):

    def __init__(self, address: str, logger = None):
        self._logger = logger or logging.getLogger(__name__)
        self._ev3_color_sensor = ColorSensor(address=address)

    def distance_centimeters(self) -> float: 
        _reflected_light_intensity = self._ev3_color_sensor.reflected_light_intensity
        if _reflected_light_intensity <= 0:
            return 255.0
        else:
            # Experimentally found logarithmic function for distance: 
            return round( ( math.log(_reflected_light_intensity / 105)) / ( math.log(0.555) ), 1)
