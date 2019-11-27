from maze_solver.kwargs_util import KwArgsUtil
from maze_solver.maze_solver import WallDetector
from ev3.ultrasound_distance_detectors import EV3UltrasoundDistanceDetectors

class EV3WallDetector(WallDetector):

    def __init__(self, distance_sensors: EV3UltrasoundDistanceDetectors, **kwargs):
        self._distance_sensors = distance_sensors
        self._distance_treshold_to_decide_wall_is_blocked = KwArgsUtil.kwarg_or_default(9.0, 'distance_treshold_to_decide_wall_is_blocked', **kwargs)

    def is_left_blocked(self) -> bool:
        _distance = self._distance_sensors.get_distances()['left']
        print('DEBUG - EV3WallDetector: left distance = {}'.format(_distance))
        return _distance < self._distance_treshold_to_decide_wall_is_blocked
    
    def is_front_blocked(self) -> bool:
        _distance = self._distance_sensors.get_distances()['front']
        print('DEBUG - EV3WallDetector: front distance = {}'.format(_distance))
        return _distance < self._distance_treshold_to_decide_wall_is_blocked
    
    def is_right_blocked(self) -> bool:
        _distance = self._distance_sensors.get_distances()['right']
        print('DEBUG - EV3WallDetector: right distance = {}'.format(_distance))
        return _distance < self._distance_treshold_to_decide_wall_is_blocked
