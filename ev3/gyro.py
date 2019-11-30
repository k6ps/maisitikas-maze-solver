import time
import logging
from ev3dev2.sensor.lego import GyroSensor
from ev3.simple_worker_thread import SimplePeriodicWorkerThread

class Gyro(SimplePeriodicWorkerThread):

    def __init__(self, logger=None):
        self._logger = logger or logging.getLogger(__name__)
        super().__init__(thread_name = 'EV3Gyro')
        self._gyro = GyroSensor(address='in1')
        self._gyro.mode = GyroSensor.MODE_GYRO_ANG
        self._gyro.reset()
        self._angle = 0

    def perform_cycle(self):
        # Occasionally, the EV3 gyro sensor gives some exeptions. Usually it happens
        # for a few seconds after it is started. Maybe its initialization is not yet 
        # complete. According to experiments, we can ignore this.
        try:
            self._angle = self._gyro.angle
        except:
            self._logger.warning('Unable to get angle from EV3 gyro sensor')

    def get_orientation(self):
        # It is ok to read a little outdated data
        return self._angle
        