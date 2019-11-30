import math
import time
import random
import enum
import logging
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, MoveSteering, SpeedRPM
from ev3.ultrasound_distance_detectors import EV3UltrasoundDistanceDetectors
from ev3.gyro import Gyro
from ev3.position_corrector import PositionCorrector
from ev3.steering import Steering
from maze_solver.maze_solver import Motors
from maze_solver.kwargs_util import KwArgsUtil


class EV3Motors(Motors):

    def __init__(
        self, 
        distance_sensors: EV3UltrasoundDistanceDetectors, 
        gyro: Gyro,
        logger = None,
        **kwargs
    ):
        self._logger = logger or logging.getLogger(__name__)
        self._distance_sensors = distance_sensors
        self._gyro = gyro
        self._motor_pair = MoveSteering(OUTPUT_A, OUTPUT_B)
        self._position_corrector = PositionCorrector(self._motor_pair, self._gyro, self._distance_sensors)
        self._maze_square_length_mm = KwArgsUtil.kwarg_or_default(180, 'maze_square_length_mm', **kwargs)
        self._move_forward_speed_rpm = KwArgsUtil.kwarg_or_default(50, 'move_forward_speed_rpm', **kwargs)
        self._motor_pair_polarity_factor = KwArgsUtil.kwarg_or_default(-1, 'motor_pair_polarity_factor', **kwargs)
        self._turn_speed_rpm = KwArgsUtil.kwarg_or_default(50, 'turn_speed_rpm', **kwargs)
        self._wheel_diameter_mm = KwArgsUtil.kwarg_or_default(56, 'wheel_diameter_mm', **kwargs)
        self._wheel_circumference_mm = math.pi * self._wheel_diameter_mm
        self._wheelbase_width_at_centers_mm = KwArgsUtil.kwarg_or_default(97.5, 'wheelbase_width_at_centers_mm', **kwargs)

    def _log_distances_and_angle(self, phase: str, distances: dict, angle: int):
        self._logger.debug('Distances {}: left={}, right={}, front={}'.format(
            phase,
            distances['left'],
            distances['right'],
            distances['front']
        ))
        self._logger.debug('Gyro angle {}={}'.format(phase, angle))

    def _move_forward_mm(self, distance_mm: float, speed_rpm: int):
        _speed = SpeedRPM(speed_rpm * self._motor_pair_polarity_factor)
        _rotations = distance_mm / self._wheel_circumference_mm
        self._motor_pair.on_for_rotations(
            steering=Steering.STRAIGHT.value, 
            speed=_speed, 
            rotations=_rotations,
            brake=True, block=True
        )

    def _turn_on_spot_deg(self, direction: Steering, degrees: int):
        _rotations = (self._wheelbase_width_at_centers_mm * degrees) / (self._wheel_diameter_mm * 360)
        self._motor_pair.on_for_rotations(
            steering=direction.value, 
            speed=SpeedRPM(self._turn_speed_rpm), 
            rotations=_rotations
        )

    def move_forward(self):
        self._logger.debug('Move_forward')
        _distances_before = self._distance_sensors.get_distances()
        _angle_before = self._gyro.get_orientation()
        self._log_distances_and_angle('before', _distances_before, _angle_before)
        self._move_forward_mm(distance_mm=self._maze_square_length_mm, speed_rpm=self._move_forward_speed_rpm)
        _distances_after = self._distance_sensors.get_distances()
        _angle_after = self._gyro.get_orientation()
        self._log_distances_and_angle('after move before correction', _distances_after, _angle_after)
        self._position_corrector.correct_after_move_forward(_distances_before, _angle_before, _distances_after, _angle_after)
        self._logger.debug('Move_forward done')

    def turn_left(self):
        self._logger.debug('turn_left')
        _distances_before = self._distance_sensors.get_distances()
        _angle_before = self._gyro.get_orientation()
        self._log_distances_and_angle('before', _distances_before, _angle_before)
        self._turn_on_spot_deg(direction=Steering.LEFT_ON_SPOT, degrees=90)
        _distances_after = self._distance_sensors.get_distances()
        _angle_after = self._gyro.get_orientation()
        self._log_distances_and_angle('after move before correction', _distances_after, _angle_after)
        self._position_corrector.correct_after_turn_left(_distances_before, _angle_before, _distances_after, _angle_after)
        self._logger.debug('turn_left done')

    def turn_right(self):
        self._logger.debug('turn_right')
        _distances_before = self._distance_sensors.get_distances()
        _angle_before = self._gyro.get_orientation()
        self._log_distances_and_angle('before', _distances_before, _angle_before)
        self._turn_on_spot_deg(direction=Steering.RIGHT_ON_SPOT, degrees=90)
        _distances_after = self._distance_sensors.get_distances()
        _angle_after = self._gyro.get_orientation()
        self._log_distances_and_angle('after move before correction', _distances_after, _angle_after)
        self._position_corrector.correct_after_turn_right(_distances_before, _angle_before, _distances_after, _angle_after)
        self._logger.debug('turn_right done')

    def turn_back(self):
        self._logger.debug('turn_back')
        _distances_before = self._distance_sensors.get_distances()
        _angle_before = self._gyro.get_orientation()
        self._log_distances_and_angle('before', _distances_before, _angle_before)
        _steering = random.choice([Steering.LEFT_ON_SPOT, Steering.RIGHT_ON_SPOT])
        self._turn_on_spot_deg(direction=_steering, degrees=180)
        _distances_after = self._distance_sensors.get_distances()
        _angle_after = self._gyro.get_orientation()
        self._log_distances_and_angle('after move before correction', _distances_after, _angle_after)
        self._position_corrector.correct_after_turn_back(_distances_before, _angle_before, _distances_after, _angle_after)
        self._logger.debug('turn_back done')

    def no_turn(self):
        pass
