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


class EV3Motors(Motors):

    def __init__(
        self, 
        distance_sensors: EV3UltrasoundDistanceDetectors, 
        gyro: Gyro,
        logger = None
    ):
        self._logger = logger or logging.getLogger(__name__)
        self._distance_sensors = distance_sensors
        self._gyro = gyro
        self._motor_pair = MoveSteering(OUTPUT_A, OUTPUT_B)
        self._position_corrector = PositionCorrector(self._motor_pair, self._gyro, self._distance_sensors)
        self._motor_degrees_for_90_degree_turn = 131.5
        self._maze_square_length_mm = 180
        self._move_forward_speed_percent = 50
        self._move_forward_speed_factor = -1
        self._turn_speed_percent = 50
        self._wheel_diameter_mm = 56
        self._wheel_circumference_mm = math.pi * self._wheel_diameter_mm
        self._wheelbase_width_mm = 130.2

    def _get_current_time_milliseconds(self):
        return int(round(time.time() * 1000))

    def _get_move_square_forward_time_sec(self, front_distance_mm: float, no_of_squares: int = 1):
        _length_mm = self._maze_square_length_mm
        _rotations = (no_of_squares * _length_mm) / self._wheel_circumference_mm
        return _rotations / (self._move_forward_speed_percent / 60)

    def move_forward(self, no_of_squares: int = 1):
        self._logger.debug('Move_forward')
        _distances_before = self._distance_sensors.get_distances()
        self._logger.debug('Distances before: left={}, right={}, front={}'.format(
            _distances_before['left'],
            _distances_before['right'],
            _distances_before['front']
        ))
        _angle_before = self._gyro.get_orientation()
        _speed = SpeedRPM(self._move_forward_speed_percent * self._move_forward_speed_factor)
        _move_time_sec = self._get_move_square_forward_time_sec(
            front_distance_mm = _distances_before['front'] * 10, 
            no_of_squares = no_of_squares
        )
        self._motor_pair.on_for_seconds(
            steering=Steering.STRAIGHT.value, 
            speed=_speed, 
            seconds=_move_time_sec,
            brake=True, block=True
        )
        _angle_after = self._gyro.get_orientation()
        self._logger.debug('Gyro angle change before correction={}'.format(_angle_after - _angle_before))
        _distances_after = self._distance_sensors.get_distances()
        self._logger.debug('Distances after move before correction: left={}, right={}, front={}'.format(
            _distances_after['left'],
            _distances_after['right'],
            _distances_after['front']
        ))
        self._position_corrector.correct_after_move_forward(_distances_before, _angle_before, _distances_after, _angle_after)
        self._logger.debug('Move_forward done')

    def turn_left(self):
        self._logger.debug('turn_left')
        _angle_before = self._gyro.get_orientation()
        _distances_before = self._distance_sensors.get_distances()
        self._logger.debug('Distances before: left={}, right={}, front={}'.format(
            _distances_before['left'],
            _distances_before['right'],
            _distances_before['front']
        ))
        _compensating_factor = 4.0
        self._logger.debug('Compensating factor={}'.format(_compensating_factor))
        self._motor_pair.on_for_degrees(
            steering = Steering.LEFT_ON_SPOT.value, 
            speed = SpeedRPM(self._turn_speed_percent), 
            degrees = self._motor_degrees_for_90_degree_turn + _compensating_factor, 
            brake=True, block=True
        )
        _angle_after = self._gyro.get_orientation()
        self._logger.debug('Gyro angle change={}'.format(_angle_after - _angle_before))
        _distances_after = self._distance_sensors.get_distances()
        self._logger.debug('Distances after: left={}, right={}, front={}'.format(
            _distances_after['left'],
            _distances_after['right'],
            _distances_after['front']
        ))
        self._position_corrector.correct_after_turn_left(_distances_before, _angle_before, _distances_after, _angle_after)
        self._logger.debug('turn_left done')

    def turn_right(self):
        self._logger.debug('turn_right')
        _angle_before = self._gyro.get_orientation()
        _distances_before = self._distance_sensors.get_distances()
        self._logger.debug('Distances before: left={}, right={}, front={}'.format(
            _distances_before['left'],
            _distances_before['right'],
            _distances_before['front']
        ))
        _compensating_factor = 1.0
        self._logger.debug('Compensating factor={}'.format(_compensating_factor))
        self._motor_pair.on_for_degrees(
            steering = Steering.RIGHT_ON_SPOT.value, 
            speed = SpeedRPM(self._turn_speed_percent), 
            degrees = self._motor_degrees_for_90_degree_turn + _compensating_factor, 
            brake=True, block=True
        )
        _angle_after = self._gyro.get_orientation()
        self._logger.debug('Gyro angle change={}'.format(_angle_after - _angle_before))
        _distances_after = self._distance_sensors.get_distances()
        self._logger.debug('Distances after: left={}, right={}, front={}'.format(
            _distances_after['left'],
            _distances_after['right'],
            _distances_after['front']
        ))
        self._position_corrector.correct_after_turn_right(_distances_before, _angle_before, _distances_after, _angle_after)
        self._logger.debug('turn_right done')

    def turn_back(self):
        self._logger.debug('turn_back')
        _angle_before = self._gyro.get_orientation()
        _distances_before = self._distance_sensors.get_distances()
        self._logger.debug('Distances before: left={}, right={}, front={}'.format(
            _distances_before['left'],
            _distances_before['right'],
            _distances_before['front']
        ))
        _compensating_factor_left = 4.0
        _compensating_factor_right = 1.0
        self._logger.debug('Compensating factor left={}'.format(_compensating_factor_left))
        self._logger.debug('Compensating factor right={}'.format(_compensating_factor_right))
        _steering = random.choice([Steering.LEFT_ON_SPOT, Steering.RIGHT_ON_SPOT])
        _compensating_factor = _compensating_factor_left if _steering == Steering.LEFT_ON_SPOT else _compensating_factor_right
        self._motor_pair.on_for_degrees(
            steering = _steering.value, 
            speed = SpeedRPM(self._turn_speed_percent), 
            degrees = 2 * (self._motor_degrees_for_90_degree_turn + _compensating_factor), 
            brake=True, block=True
        )
        _angle_after = self._gyro.get_orientation()
        self._logger.debug('Gyro angle change={}'.format(_angle_after - _angle_before))
        _distances_after = self._distance_sensors.get_distances()
        self._logger.debug('Distances after: left={}, right={}, front={}'.format(
            _distances_after['left'],
            _distances_after['right'],
            _distances_after['front']
        ))
        self._position_corrector.correct_after_turn_back(_distances_before, _angle_before, _distances_after, _angle_after)
        self._logger.debug('turn_back done')

    def no_turn(self):
        pass
