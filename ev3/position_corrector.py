import time
import logging
import math
from maze_solver.kwargs_util import KwArgsUtil
from ev3.steering import Steering
from ev3.gyro import Gyro
from ev3.distance_detectors import EV3DistanceDetectors
from ev3dev2.motor import MoveSteering, SpeedRPM


class PositionCorrector(object):

    def __init__(
        self, 
        ev3_motor_pair: MoveSteering, 
        ev3_gyro: Gyro, 
        logger = None, 
        **kwargs
    ):
        self._logger = logger or logging.getLogger(__name__)
        self._motor_pair = ev3_motor_pair
        self._gyro = ev3_gyro
        self._wheel_diameter_mm = KwArgsUtil.kwarg_or_default(56, 'wheel_diameter_mm', **kwargs)
        self._wheelbase_width_at_centers_mm = KwArgsUtil.kwarg_or_default(97.5, 'wheelbase_width_at_centers_mm', **kwargs)
        self._wheel_circumference_mm = math.pi * self._wheel_diameter_mm
        self._ideal_side_turn_angle = KwArgsUtil.kwarg_or_default(90, 'ideal_side_turn_angle', **kwargs)
        self._ideal_distance_cm = KwArgsUtil.kwarg_or_default(2.0, 'ideal_distance_cm', **kwargs)
        self._correction_speed_rpm = KwArgsUtil.kwarg_or_default(25, 'correction_speed_rpm', **kwargs)
        self._move_forward_speed_factor = KwArgsUtil.kwarg_or_default(1, 'move_forward_speed_factor', **kwargs)
        self._turn_side_bad_angle_treshold = KwArgsUtil.kwarg_or_default(15, 'turn_side_bad_angle_treshold', **kwargs)

    def _has_gyro_angle_changed_too_much_for_move_forward(self, angle_before: int, angle_after: int):
        _move_forward_bad_angle_min_treshold = 5
        return abs(angle_after - angle_before) > _move_forward_bad_angle_min_treshold

    def _has_gyro_angle_changed_too_little_for_side_turn(self, angle_before: int, angle_after: int):
        return abs(angle_after - angle_before) < (self._ideal_side_turn_angle - self._turn_side_bad_angle_treshold)

    def _has_gyro_angle_changed_too_much_for_side_turn(self, angle_before: int, angle_after: int):
        return abs(angle_after - angle_before) > (self._ideal_side_turn_angle + self._turn_side_bad_angle_treshold)

    def _correct_front_distance(self, front_distance_cm: float):
        _distance_to_compensate_mm = (front_distance_cm - self._ideal_distance_cm) * 10
        self._logger.debug('Need to correct front distance for {} mm'.format(_distance_to_compensate_mm))
        self._motor_pair.on_for_rotations(
            steering=Steering.STRAIGHT.value, 
            speed=SpeedRPM(self._correction_speed_rpm * self._move_forward_speed_factor), 
            rotations=(_distance_to_compensate_mm / self._wheel_circumference_mm),
            brake=True, block=True
        )

    def _correct_bad_angle_after_turn(self, angle_before: int, angle_after: int, steering: Steering):
        _min_angle_correction = 15
        _angle_diff = abs(self._ideal_side_turn_angle - abs(angle_after - angle_before))
        if _angle_diff < _min_angle_correction:
            _angle_diff = _min_angle_correction
        self._logger.debug('Angle diff = {}'.format(_angle_diff))
        _rotations = (self._wheelbase_width_at_centers_mm * _angle_diff) / (self._wheel_diameter_mm * 360)
        self._motor_pair.on_for_rotations(
            steering=steering.value, 
            speed=SpeedRPM(self._correction_speed_rpm), 
            rotations=_rotations
        )

    def _recover_from_hitting_wall(self, angle_before: int, angle_after: int, recursion_count: int):

        _back_off_from_wall_distance_cm = 2.0
        _base_front_travel_distance_after_backing_off_and_correctin_angle_cm = 9.0
        _max_recursion_count = 3

        def _back_off_from_wall():
            self._motor_pair.on_for_rotations(
                steering=Steering.STRAIGHT.value, 
                speed=SpeedRPM(self._correction_speed_rpm * self._move_forward_speed_factor), 
                rotations=-((_back_off_from_wall_distance_cm + recursion_count) * 10 / self._wheel_circumference_mm),
                brake=True, block=True
            )

        def _correct_angle():
            _angle_diff = angle_after - angle_before
            _steering = Steering.LEFT_ON_SPOT if _angle_diff > 0 else Steering.RIGHT_ON_SPOT
            _rotations = (self._wheelbase_width_at_centers_mm * abs(_angle_diff)) / (self._wheel_diameter_mm * 360)
            self._motor_pair.on_for_rotations(
                steering=_steering.value, 
                speed=SpeedRPM(self._correction_speed_rpm), 
                rotations=_rotations
            )

        def _move_forward_to_hopefully_correct_position(recursion_count: int):
            _front_distance = _base_front_travel_distance_after_backing_off_and_correctin_angle_cm - recursion_count
            self._motor_pair.on_for_rotations(
                steering=Steering.STRAIGHT.value, 
                speed=SpeedRPM(self._correction_speed_rpm * self._move_forward_speed_factor), 
                rotations=_front_distance * 10 / self._wheel_circumference_mm
            )

        def _recover_if_hit_wall_again_while_recovering(recursion_count: int):
            _angle_after_front_distance_correction = self._gyro.get_orientation()
            if (self._has_gyro_angle_changed_too_much_for_move_forward(angle_before, _angle_after_front_distance_correction)):
                self._logger.debug('Bad gyro angle when recovering from hitting wall. I have hit the wall again or failed to recover!')
                self._recover_from_hitting_wall(angle_before, _angle_after_front_distance_correction, recursion_count + 1)
            
        if recursion_count >= _max_recursion_count:
            self._logger.debug('I have reached my recursion limit! Just continuing and hoping for the best.')
            return
        _back_off_from_wall()
        _correct_angle()
        _move_forward_to_hopefully_correct_position(recursion_count=recursion_count)
        time.sleep(0.1)
        _recover_if_hit_wall_again_while_recovering(recursion_count=recursion_count)

    def _correct_side_distance(self, distances_after):
        _side_distance_correction_fix_degrees = 10
        self._logger.debug('I am in between two side walls. Checking if i am too close to one..')
        if distances_after['left'] < self._ideal_distance_cm:
            self._logger.debug('I am too close to left wall. Correcting angle a bit..')
            self._motor_pair.on_for_degrees(
                steering=Steering.RIGHT_ON_SPOT.value, 
                speed=SpeedRPM(self._correction_speed_rpm), 
                degrees=_side_distance_correction_fix_degrees
            )
        elif distances_after['right'] < self._ideal_distance_cm:
            self._logger.debug('I am too close to right wall. Correcting angle a bit..')
            self._motor_pair.on_for_degrees(
                steering=Steering.LEFT_ON_SPOT.value, 
                speed=SpeedRPM(self._correction_speed_rpm), 
                degrees=_side_distance_correction_fix_degrees
            )
        else:
            self._logger.debug('No problem, i am fine between the walls.')

    def correct_after_move_forward(self, 
        angle_before: int, 
        distances_after: dict, 
        angle_after: int 
    ):
        _max_reliable_distance_cm = 5
        self._logger.debug('correct_after_move_forward')
        _is_angle_bad = self._has_gyro_angle_changed_too_much_for_move_forward(angle_before, angle_after)
        if _is_angle_bad:
            self._logger.debug('Bad gyro angle. I have hit the wall')
            self._recover_from_hitting_wall(angle_before, angle_after, 1)
        else:
            if distances_after['front'] <= _max_reliable_distance_cm and distances_after['front'] != self._ideal_distance_cm:
                self._logger.debug('Bad front distance!')
                self._correct_front_distance(distances_after['front'])
            if distances_after['left'] <= _max_reliable_distance_cm and distances_after['right'] <= _max_reliable_distance_cm:
                self._correct_side_distance(distances_after)
        self._logger.debug('correct_after_move_forward done')

    def correct_after_turn_left(self, 
        angle_before: int, 
        angle_after: int, 
    ):
        self._logger.debug('correct_after_turn_left')
        _is_angle_too_little = self._has_gyro_angle_changed_too_little_for_side_turn(angle_before, angle_after)
        _is_angle_too_big = self._has_gyro_angle_changed_too_much_for_side_turn(angle_before, angle_after)
        if _is_angle_too_little:
            self._logger.debug('Bad gyro angle - too little!')
            self._correct_bad_angle_after_turn(angle_before, angle_after, Steering.LEFT_ON_SPOT)
        elif _is_angle_too_big:
            self._logger.debug('Bad gyro angle - too big!')
            self._correct_bad_angle_after_turn(angle_before, angle_after, Steering.RIGHT_ON_SPOT)
        self._logger.debug('correct_after_turn_left done')

    def correct_after_turn_right(self, 
        angle_before: int, 
        angle_after: int, 
    ):
        self._logger.debug('correct_after_turn_right')
        _is_angle_too_little = self._has_gyro_angle_changed_too_little_for_side_turn(angle_before, angle_after)
        _is_angle_too_big = self._has_gyro_angle_changed_too_much_for_side_turn(angle_before, angle_after)
        if _is_angle_too_little:
            self._logger.debug('Bad gyro angle - too little!')
            self._correct_bad_angle_after_turn(angle_before, angle_after, Steering.RIGHT_ON_SPOT)
        elif _is_angle_too_big:
            self._logger.debug('Bad gyro angle - too big!')
            self._correct_bad_angle_after_turn(angle_before, angle_after, Steering.LEFT_ON_SPOT)
        self._logger.debug('correct_after_turn_right done')
