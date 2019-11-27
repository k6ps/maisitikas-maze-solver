import time
import logging
import threading
from ev3dev2.sensor.lego import GyroSensor

class Gyro(threading.Thread):

    def __init__(self, logger=None):
        self._logger = logger or logging.getLogger(__name__)
        threading.Thread.__init__(self)
        self.setName('EV3Gyro')
        self._stop_command_received = False
        self._reading_cycle_length_ms = 100
        self._gyro = GyroSensor(address='in1')
        self._gyro.mode = GyroSensor.MODE_GYRO_ANG
        self._gyro.reset()
        self._angle = 0

    def _get_current_time_milliseconds(self):
        return int(round(time.time() * 1000))

    def _wait_until_end_of_cycle_time(self, cycle_start_time):
        _cycle_end_time = self._get_current_time_milliseconds()
        _cycle_time = _cycle_end_time - cycle_start_time
        if (_cycle_time < self._reading_cycle_length_ms):
            time.sleep((self._reading_cycle_length_ms - _cycle_time) * 0.001)

    def run(self):
        self._logger.debug('Starting')
        while (self._stop_command_received == False):
            _cycle_start_time = self._get_current_time_milliseconds()
            try:
                self._angle = self._gyro.angle
            except:
                self._logger.warning('Unable to get angle from EV3 gyro sensor')
            self._wait_until_end_of_cycle_time(_cycle_start_time)
        self._logger.debug('Stopped')

    def stop(self):
        self._logger.debug('Stop requested')
        self._stop_command_received = True

    def get_orientation(self):
        return self._angle

    def reset(self):
        self._gyro.reset()
        