import logging
from maze_solver.kwargs_util import KwArgsUtil
from ev3dev2.motor import MoveSteering, SpeedRPM


class PositionCorrector(object):

    def __init__(self, ev3_motor_pair: MoveSteering, logger = None, **kwargs):
        self._logger = logger or logging.getLogger(__name__)
        self._ev3_motor_pair = ev3_motor_pair
        self._bad_distance_lower_treshold_cm = KwArgsUtil.kwarg_or_default(4.0, 'bad_distance_lower_treshold_cm', **kwargs)
        self._bad_distance_upper_treshold_cm = KwArgsUtil.kwarg_or_default(16.0, 'bad_distance_upper_treshold_cm', **kwargs)
        self._too_small_distance_upper_treshold_cm = KwArgsUtil.kwarg_or_default(3.0, 'too_small_distance_upper_treshold_cm', **kwargs)
        self._min_reliable_distance_sensor_value_cm = KwArgsUtil.kwarg_or_default(3.1, 'min_reliable_distance_sensor_value_cm', **kwargs)
        self._square_length_cm = KwArgsUtil.kwarg_or_default(18.0, 'square_length_cm', **kwargs)
        self._move_forward_bad_angle_min_treshold = KwArgsUtil.kwarg_or_default(15, 'move_forward_bad_angle_min_treshold', **kwargs)
        self._turn_side_bad_angle_max_treshold = KwArgsUtil.kwarg_or_default(55, 'turn_side_bad_angle_max_treshold', **kwargs)
        self._turn_back_bad_angle_max_treshold = KwArgsUtil.kwarg_or_default(120, 'turn_back_bad_angle_max_treshold', **kwargs)

    def _get_distance_remainder_cm(self, distance_cm: float) -> float:
        return distance_cm % self._square_length_cm

    def _is_bad_distance(self, distance_cm: float) -> bool:
        _distance_remainder_cm = self._get_distance_remainder_cm(distance_cm)
        _is_above_lower_treshold = _distance_remainder_cm > self._bad_distance_lower_treshold_cm
        _is_below_upper_treshhold = _distance_remainder_cm < self._bad_distance_upper_treshold_cm
        return _is_above_lower_treshold and _is_below_upper_treshhold

    def _is_too_small_or_below_min_reliable(self, distance_cm: float) -> bool:
        if distance_cm < self._min_reliable_distance_sensor_value_cm:
            return True
        elif self._get_distance_remainder_cm(distance_cm) < self._too_small_distance_upper_treshold_cm:
            return True
        else:
            return False

    def _has_gyro_angle_changed_too_much_for_move_forward(self, angle_before: int, angle_after: int):
        return abs(angle_after - angle_before) > self._move_forward_bad_angle_min_treshold

    def _has_gyro_angle_changed_too_little_for_side_turn(self, angle_before: int, angle_after: int):
        return abs(angle_after - angle_before) < self._turn_side_bad_angle_max_treshold

    def _has_gyro_angle_changed_too_little_for_back_turn(self, angle_before: int, angle_after: int):
        return abs(angle_after - angle_before) < self._turn_back_bad_angle_max_treshold

    def _is_only_front_distance_bad(self, distances: dict) -> bool:
        _is_front_bad = self._is_bad_distance(distances['front'])
        _is_left_bad = self._is_bad_distance(distances['left'])
        _is_right_bad = self._is_bad_distance(distances['right'])
        return _is_front_bad and (not _is_left_bad) and (not _is_right_bad)

    def _is_front_and_right_bad_and_left_too_close(self, distances: dict) -> bool:
        _is_front_bad = self._is_bad_distance(distances['front'])
        _is_left_too_close = self._is_too_small_or_below_min_reliable(distances['left'])
        _is_right_bad = self._is_bad_distance(distances['right'])
        return _is_front_bad and _is_left_too_close and _is_right_bad

    def _is_front_and_left_bad_and_right_too_close(self, distances: dict) -> bool:
        _is_front_bad = self._is_bad_distance(distances['front'])
        _is_right_too_close = self._is_too_small_or_below_min_reliable(distances['right'])
        _is_left_bad = self._is_bad_distance(distances['left'])
        return _is_front_bad and _is_right_too_close and _is_left_bad

    def _is_left_bad_and_right_too_close_only(self, distances: dict) -> bool:
        _is_front_bad = self._is_bad_distance(distances['front'])
        _is_right_too_close = self._is_too_small_or_below_min_reliable(distances['right'])
        _is_left_bad = self._is_bad_distance(distances['left'])
        return (not _is_front_bad) and _is_right_too_close and _is_left_bad

    def _is_right_bad_and_left_too_close_only(self, distances: dict) -> bool:
        _is_front_bad = self._is_bad_distance(distances['front'])
        _is_left_too_close = self._is_too_small_or_below_min_reliable(distances['left'])
        _is_right_bad = self._is_bad_distance(distances['right'])
        return (not _is_front_bad) and _is_left_too_close and _is_right_bad

    def _log_distance_remainders(self, distances: dict):
        _front_distance_remainder_cm = self._get_distance_remainder_cm(distances['front'])
        _left_distance_remainder_cm = self._get_distance_remainder_cm(distances['left'])
        _right_distance_remainder_cm = self._get_distance_remainder_cm(distances['right'])
        self._logger.debug('Distance remainders front={}, left={}, right={}'.format(
            _front_distance_remainder_cm,
            _left_distance_remainder_cm,
            _right_distance_remainder_cm
        ))

    def _correct_distances(self, distances: dict):
        if self._is_only_front_distance_bad(distances):
            self._logger.debug('Bad front distance. I am at good angle but too far')
        elif self._is_front_and_right_bad_and_left_too_close(distances):
            self._logger.debug('Bad front and right distances, small left distance. I am at bad angle too much to the right')
        elif self._is_front_and_left_bad_and_right_too_close(distances):
            self._logger.debug('Bad front and left distances, small right distance. I am at bad angle too much to the left')
        elif self._is_left_bad_and_right_too_close_only(distances):
            self._logger.debug('Bad left distance, small right distance. I am at good angle but too much at right')
        elif self._is_right_bad_and_left_too_close_only(distances):
            self._logger.debug('Bad right distance, small left distance. I am at good angle but too much at left')
        else:
            self._logger.debug('All distances are good')

    def correct_after_move_forward(self, 
        distances_before: dict, 
        angle_before: int, 
        distances_after: dict, 
        angle_after: int 
    ):
        self._logger.debug('correct_after_move_forward')
        self._log_distance_remainders(distances_after)
        _is_angle_bad = self._has_gyro_angle_changed_too_much_for_move_forward(angle_before, angle_after)
        if _is_angle_bad:
            self._logger.debug('Bad gyro angle. I have hit the wall')
        else:
            self._correct_distances(distances_after)
        self._logger.debug('correct_after_move_forward done')

    def correct_after_turn_left(self, 
        distances_before: dict, 
        angle_before: int, 
        distances_after: dict, 
        angle_after: int, 
        can_move_backward: bool = False
    ):
        self._logger.debug('correct_after_turn_left')
        self._log_distance_remainders(distances_after)
        _is_angle_bad = self._has_gyro_angle_changed_too_little_for_side_turn(angle_before, angle_after)
        if _is_angle_bad:
            self._logger.debug('Bad gyro angle. I hit the wall on left turn and turned too little.')
        else:
            self._correct_distances(distances_after)
        self._logger.debug('correct_after_turn_left done')

    def correct_after_turn_right(self, 
        distances_before: dict, 
        angle_before: int, 
        distances_after: dict, 
        angle_after: int, 
        can_move_backward: bool = False
    ):
        self._logger.debug('correct_after_turn_right')
        self._log_distance_remainders(distances_after)
        _is_angle_bad = self._has_gyro_angle_changed_too_little_for_side_turn(angle_before, angle_after)
        if _is_angle_bad:
            self._logger.debug('Bad gyro angle. I hit the wall on right turn and turned too little.')
        else:
            self._correct_distances(distances_after)
        self._logger.debug('correct_after_turn_right done')

    def correct_after_turn_back(self, 
        distances_before: dict, 
        angle_before: int, 
        distances_after: dict, 
        angle_after: int, 
    ):
        self._logger.debug('correct_after_turn_back')
        self._log_distance_remainders(distances_after)
        _is_angle_bad = self._has_gyro_angle_changed_too_little_for_back_turn(angle_before, angle_after)
        if _is_angle_bad:
            self._logger.debug('Bad gyro angle. I hit the wall on back turn and turned too little.')
        else:
            self._correct_distances(distances_after)
        self._logger.debug('correct_after_turn_back done')
