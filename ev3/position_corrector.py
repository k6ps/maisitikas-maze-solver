import logging
import math
from maze_solver.kwargs_util import KwArgsUtil
from ev3.steering import Steering
from ev3.gyro import Gyro
from ev3dev2.motor import MoveSteering, SpeedRPM


class PositionCorrector(object):

    def __init__(self, ev3_motor_pair: MoveSteering, ev3_gyro: Gyro, logger = None, **kwargs):
        self._logger = logger or logging.getLogger(__name__)
        self._motor_pair = ev3_motor_pair
        self._gyro = ev3_gyro
        self._wheel_diameter_mm = KwArgsUtil.kwarg_or_default(56, 'wheel_diameter_mm', **kwargs)
        self._wheelbase_width_at_centers_mm = KwArgsUtil.kwarg_or_default(130.2, 'wheelbase_width_at_centers_mm', **kwargs)
        self._wheel_circumference_mm = math.pi * self._wheel_diameter_mm
        self._ideal_side_turn_angle = KwArgsUtil.kwarg_or_default(80, 'ideal_side_turn_angle', **kwargs)
        self._ideal_distance_cm = KwArgsUtil.kwarg_or_default(3.0, 'ideal_distance_cm', **kwargs)
        self._min_front_distance_correction_mm = KwArgsUtil.kwarg_or_default(5.0, 'min_front_distance_correction_mm', **kwargs)
        self._correction_speed_rpm = KwArgsUtil.kwarg_or_default(15, 'correction_speed_rpm', **kwargs)
        self._move_forward_speed_factor = KwArgsUtil.kwarg_or_default(-1, 'move_forward_speed_factor', **kwargs)
        self._bad_distance_lower_treshold_cm = KwArgsUtil.kwarg_or_default(4.0, 'bad_distance_lower_treshold_cm', **kwargs)
        self._bad_distance_upper_treshold_cm = KwArgsUtil.kwarg_or_default(15.0, 'bad_distance_upper_treshold_cm', **kwargs)
        self._too_small_distance_upper_treshold_cm = KwArgsUtil.kwarg_or_default(3.2, 'too_small_distance_upper_treshold_cm', **kwargs)
        self._min_reliable_distance_sensor_value_cm = KwArgsUtil.kwarg_or_default(3.2, 'min_reliable_distance_sensor_value_cm', **kwargs)
        self._square_length_cm = KwArgsUtil.kwarg_or_default(18.0, 'square_length_cm', **kwargs)
        self._move_forward_bad_angle_min_treshold = KwArgsUtil.kwarg_or_default(15, 'move_forward_bad_angle_min_treshold', **kwargs)
        self._turn_side_bad_angle_max_treshold = KwArgsUtil.kwarg_or_default(65, 'turn_side_bad_angle_max_treshold', **kwargs)
        self._turn_back_bad_angle_max_treshold = KwArgsUtil.kwarg_or_default(120, 'turn_back_bad_angle_max_treshold', **kwargs)
        self._max_front_distance_to_correct_forward_cm = KwArgsUtil.kwarg_or_default(7.0, 'max_front_distance_to_correct_forward_cm', **kwargs)
        self._max_front_distance_to_correct_backward_cm = KwArgsUtil.kwarg_or_default(21.0, 'max_front_distance_to_correct_backward_cm', **kwargs)
        self._min_front_distance_to_correct_backward_cm = KwArgsUtil.kwarg_or_default(17.0, 'max_front_distance_to_correct_backward_cm', **kwargs)

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

    def _correct_front_distance(self, front_distance_cm: float):
        _distance_to_compensate_mm = (front_distance_cm - self._ideal_distance_cm) * 10
        self._logger.debug('Distance to compensate = {} mm'.format(_distance_to_compensate_mm))
        if abs(_distance_to_compensate_mm) > self._min_front_distance_correction_mm:
            self._logger.debug('Need to correct front distance for {} mm'.format(_distance_to_compensate_mm))
            self._motor_pair.on_for_rotations(
                steering=Steering.STRAIGHT.value, 
                speed=SpeedRPM(self._correction_speed_rpm * self._move_forward_speed_factor), 
                rotations=(_distance_to_compensate_mm / self._wheel_circumference_mm),
                brake=True, block=True
            )

    def _is_front_distance_too_short(self, front_distance_cm: float) -> bool:
        return front_distance_cm < (self._ideal_distance_cm + self._square_length_cm)

    def _can_front_distance_be_corrected_forward(self, front_distance_cm: float) -> bool:
        return front_distance_cm < self._max_front_distance_to_correct_forward_cm

    def _can_front_distance_be_corrected_backward(self, front_distance_cm: float) -> bool:
        _is_below_upper_limit = front_distance_cm < self._max_front_distance_to_correct_backward_cm
        _is_above_lower_limit = front_distance_cm > self._min_front_distance_to_correct_backward_cm
        return _is_below_upper_limit and _is_above_lower_limit

    def _correct_distances(self, distances_before: dict, distances_after: dict):
        if self._is_only_front_distance_bad(distances_after) and self._can_front_distance_be_corrected_forward(distances_after['front']):
            self._logger.debug('Bad front distance. I am at good angle but too far from the next front wall')
            self._correct_front_distance(distances_after['front'])
        elif self._is_left_bad_and_right_too_close_only(distances_after):
            self._logger.debug('Bad left distance, small right distance. I am at good angle but too much at right')
            self._motor_pair.on_for_degrees(
                steering=Steering.LEFT_ON_SPOT.value, 
                speed=SpeedRPM(self._correction_speed_rpm), 
                degrees=10
            )
        elif self._is_right_bad_and_left_too_close_only(distances_after):
            self._logger.debug('Bad right distance, small left distance. I am at good angle but too much at left')
            self._motor_pair.on_for_degrees(
                steering=Steering.RIGHT_ON_SPOT.value, 
                speed=SpeedRPM(self._correction_speed_rpm), 
                degrees=10
            )
        else:
            self._logger.debug('All distances are good')

    def _correct_bad_angle_after_turn(self, angle_before: int, angle_after: int, steering: Steering):
        _angle_diff = self._ideal_side_turn_angle - abs(angle_after - angle_before)
        self._logger.debug('Angle diff = {}'.format(_angle_diff))
        _rotations = (self._wheelbase_width_at_centers_mm * _angle_diff) / (self._wheel_diameter_mm * 360)
        self._motor_pair.on_for_rotations(
            steering=steering.value, 
            speed=SpeedRPM(self._correction_speed_rpm), 
            rotations=_rotations
        )

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
            if self._is_front_distance_too_short(distances_before['front']) and self._can_front_distance_be_corrected_backward(distances_before['front']):
                self._logger.debug('Too small front distance before movement. I am at good angle but too near the next front wall')
                self._correct_front_distance(self._get_distance_remainder_cm(distances_before['front']))
            self._correct_distances(distances_before, distances_after)
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
            self._correct_bad_angle_after_turn(angle_before, angle_after, Steering.LEFT_ON_SPOT)
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
            self._correct_bad_angle_after_turn(angle_before, angle_after, Steering.RIGHT_ON_SPOT)
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
        self._logger.debug('correct_after_turn_back done')
