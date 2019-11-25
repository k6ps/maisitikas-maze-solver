import time
from threading import Thread
from ev3dev2.sensor.lego import UltrasonicSensor

class EV3UltrasoundDistanceDetectors(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.setName('EV3UltrasoundDistanceDetectors')
        self._stop_command_received = False
        self._reading_cycle_length_ms = 100
        self._sensor_left = UltrasonicSensor(address='in4')
        self._sensor_front = UltrasonicSensor(address='in3')
        self._sensor_right = UltrasonicSensor(address='in2')
        self._distance_left = 255.0
        self._distance_front = 255.0
        self._distance_right = 255.0

    def _get_current_time_milliseconds(self):
        return int(round(time.time() * 1000))

    def _wait_until_end_of_cycle_time(self, cycle_start_time):
        _cycle_end_time = self._get_current_time_milliseconds()
        _cycle_time = _cycle_end_time - cycle_start_time
        if (_cycle_time < self._reading_cycle_length_ms):
            time.sleep((self._reading_cycle_length_ms - _cycle_time) * 0.001)

    def run(self):
        print('DEBUG - EV3UltrasoundDistanceDetectors: starting')
        while (self._stop_command_received == False):
            _cycle_start_time = self._get_current_time_milliseconds()
            self._distance_left = self._sensor_left.distance_centimeters
            self._distance_front = self._sensor_front.distance_centimeters
            self._distance_right = self._sensor_right.distance_centimeters
            print('DEBUG - EV3UltrasoundDistanceDetectors: left={}, front={}, right={}'.format(
                self._distance_left, 
                self._distance_front, 
                self._distance_right
            ))
            self._wait_until_end_of_cycle_time(_cycle_start_time)
        print('DEBUG - EV3UltrasoundDistanceDetectors: stopped')

    def stop(self):
        print('DEBUG - EV3UltrasoundDistanceDetectors: stop requested')
        self._stop_command_received = True

    def get_distances(self):
        # It is ok to read slightly outdated data
        return {
            'left': self._distance_left,
            'front': self._distance_front,
            'right': self._distance_right
        }
