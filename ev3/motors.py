import math
import time
import random
import enum
import logging
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, MoveSteering, SpeedRPM
from ev3.distance_detectors import EV3DistanceDetectors
from ev3.gyro import Gyro
from ev3.position_corrector import PositionCorrector
from ev3.steering import Steering
from maze_solver.maze_solver import Motors
from maze_solver.kwargs_util import KwArgsUtil


class EV3Motors(Motors):

    def __init__(
        self, 
        distance_sensors: EV3DistanceDetectors, 
        gyro: Gyro,
        logger = None,
        **kwargs
    ):
        self._logger = logger or logging.getLogger(__name__)
        self._distance_sensors = distance_sensors
        self._gyro = gyro
        self._motor_pair = MoveSteering(OUTPUT_A, OUTPUT_B)
        self._position_corrector = PositionCorrector(self._motor_pair, self._gyro)
        self._maze_square_length_mm = KwArgsUtil.kwarg_or_default(180, 'maze_square_length_mm', **kwargs)
        self._move_forward_speed_rpm = KwArgsUtil.kwarg_or_default(60, 'move_forward_speed_rpm', **kwargs)
        self._motor_pair_polarity_factor = KwArgsUtil.kwarg_or_default(1, 'motor_pair_polarity_factor', **kwargs)
        self._turn_speed_rpm = KwArgsUtil.kwarg_or_default(50, 'turn_speed_rpm', **kwargs)
        self._wheel_diameter_mm = KwArgsUtil.kwarg_or_default(56, 'wheel_diameter_mm', **kwargs)
        self._wheel_circumference_mm = math.pi * self._wheel_diameter_mm
        self._wheelbase_width_at_centers_mm = KwArgsUtil.kwarg_or_default(97.5, 'wheelbase_width_at_centers_mm', **kwargs)
        self._turns_until_next_angle_corretion = KwArgsUtil.kwarg_or_default(3, 'turns_until_next_angle_corretion', **kwargs)
        self._angle_corretcion_speed = KwArgsUtil.kwarg_or_default(25, 'angle_corretcion_speed', **kwargs)
        self._angle_correction_move_backward_mm = KwArgsUtil.kwarg_or_default(80.0, 'angle_correction_move_backward_mm', **kwargs)
        self._angle_correction_move_forward_mm = KwArgsUtil.kwarg_or_default(20.0, 'angle_correction_move_forward_mm', **kwargs)
        self._wait_for_motors_and_gyro_after_move_sec = KwArgsUtil.kwarg_or_default(0.1, 'wait_for_motors_and_gyro_after_move_sec', **kwargs)

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

    def _correct_angle_using_back_wall(self, previous_distance_to_check: float):
        if self._turns_until_next_angle_corretion <= 0:
            if previous_distance_to_check < 4:
                self._logger.debug('I am correcting my angle using the back wall...')
                self._motor_pair.on_for_rotations(
                    steering=Steering.STRAIGHT.value, 
                    speed=SpeedRPM(self._angle_corretcion_speed * -1), 
                    rotations=(self._angle_correction_move_backward_mm / self._wheel_circumference_mm),
                    brake=True, block=True
                )
                self._motor_pair.on_for_rotations(
                    steering=Steering.STRAIGHT.value, 
                    speed=SpeedRPM(self._angle_corretcion_speed * 1), 
                    rotations=(self._angle_correction_move_forward_mm / self._wheel_circumference_mm),
                    brake=True, block=True
                )
                self._turns_until_next_angle_corretion = 3
        else:
            self._turns_until_next_angle_corretion = self._turns_until_next_angle_corretion -1

    def _move(self, move_function, correct_function):
        _distances_before = self._distance_sensors.get_distances()
        _angle_before = self._gyro.get_orientation()
        self._log_distances_and_angle('before', _distances_before, _angle_before)
        move_function()
        # Allow some time for motors to stop and gyro to react
        time.sleep(self._wait_for_motors_and_gyro_after_move_sec)
        _distances_after = self._distance_sensors.get_distances()
        _angle_after = self._gyro.get_orientation()
        self._log_distances_and_angle('after move before correction', _distances_after, _angle_after)
        correct_function(distances_before=_distances_before, angle_before=_angle_before, distances_after=_distances_after, angle_after=_angle_after)


    def move_forward(self):

        def move_function():
            self._move_forward_mm(distance_mm=self._maze_square_length_mm, speed_rpm=self._move_forward_speed_rpm)

        def correct_function(angle_before, distances_after, angle_after, **kwargs):
            self._position_corrector.correct_after_move_forward(angle_before, distances_after, angle_after)

        self._logger.debug('Move_forward')
        self._move(move_function, correct_function)
        self._logger.debug('Move_forward done')

    def turn_left(self):

        def move_function():
            self._turn_on_spot_deg(direction=Steering.LEFT_ON_SPOT, degrees=74)

        def correct_function(distances_before, angle_before, angle_after, **kwargs):
            self._position_corrector.correct_after_turn_left(angle_before, angle_after)
            self._correct_angle_using_back_wall(distances_before['right'])

        self._logger.debug('turn_left')
        self._move(move_function, correct_function)
        self._logger.debug('turn_left done')

    def turn_right(self):

        def move_function():
            self._turn_on_spot_deg(direction=Steering.RIGHT_ON_SPOT, degrees=74)

        def correct_function(distances_before, angle_before, angle_after, **kwargs):
            self._position_corrector.correct_after_turn_right(angle_before, angle_after)
            self._correct_angle_using_back_wall(distances_before['left'])

        self._logger.debug('turn_right')
        self._move(move_function, correct_function)
        self._logger.debug('turn_right done')

    def turn_back(self):
        self._logger.debug('turn_back')
        _turn_method = random.choice([self.turn_left, self.turn_right])
        _turn_method()
        _turn_method()
        self._logger.debug('turn_back done')

    def no_turn(self):
        pass
