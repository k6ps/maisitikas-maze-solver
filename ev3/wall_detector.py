import time
from maze_solver.kwargs_util import KwArgsUtil
from maze_solver.maze_solver import WallDetector
from ev3.ultrasound_distance_detectors import EV3UltrasoundDistanceDetectors

class EV3WallDetector(WallDetector):

    def __init__(self, distance_sensors: EV3UltrasoundDistanceDetectors, **kwargs):
        self._distance_sensors = distance_sensors
        self._distance_treshold_to_decide_wall_is_blocked = KwArgsUtil.kwarg_or_default(9.0, 'distance_treshold_to_decide_wall_is_blocked', **kwargs)

    def _is_direction_blocked(self, direction: str):
        time.sleep(0.2)
        _distance = self._distance_sensors.get_distances()[direction]
        print('DEBUG - EV3WallDetector: {} distance = {}'.format(direction, _distance))
        return _distance < self._distance_treshold_to_decide_wall_is_blocked

    def is_left_blocked(self) -> bool:
        return self._is_direction_blocked('left')
    
    def is_front_blocked(self) -> bool:
        return self._is_direction_blocked('front')
    
    def is_right_blocked(self) -> bool:
        return self._is_direction_blocked('right')
