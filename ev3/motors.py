import math
import time
import random
import enum
import logging
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, MoveSteering, SpeedRPM
from ev3dev2.power import PowerSupply
from ev3.ultrasound_distance_detectors import EV3UltrasoundDistanceDetectors
from ev3.gyro import Gyro
from maze_solver.maze_solver import Motors


class Steering(enum.Enum):
    STRAIGHT = 0
    LEFT_ON_SPOT = -100
    RIGHT_ON_SPOT = 100


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
        self._power_supply = PowerSupply()
        self._steering_correction_motor_degrees = 10
        self._steering_correction_speed_rpm = 15
        self._motor_degrees_for_90_degree_turn = 131.5
        self._maze_square_length_mm = 180
        self._move_forward_speed_percent = 35
        self._move_forward_speed_factor = -1
        self._turn_speed_percent = 50
        self._wheel_diameter_mm = 56
        self._wheel_circumference_mm = math.pi * self._wheel_diameter_mm
        self._wheelbase_width_mm = 130.2
        self._last_time_right_corrected = False
        self._last_time_left_corrected = False

    def _get_current_time_milliseconds(self):
        return int(round(time.time() * 1000))

    def _get_move_square_forward_time_sec(self, front_distance_mm: float, no_of_squares: int = 1):
        _length_mm = self._maze_square_length_mm
        if no_of_squares == 1 and front_distance_mm < self._maze_square_length_mm:
            _length_mm = self._maze_square_length_mm - front_distance_mm
        _rotations = (no_of_squares * _length_mm) / self._wheel_circumference_mm
        return _rotations / (self._move_forward_speed_percent / 60)

    def _should_correct_to_left(self):
        return self._distance_sensors.are_n_last_left_distances_between_x_and_y()

    def _should_correct_to_right(self):
        return self._distance_sensors.are_n_last_right_distances_between_x_and_y()

    def _correct_after_move_forward(self):
        if not self._last_time_left_corrected and self._should_correct_to_left():
            self._logger.debug('Correcting to left')
            self._motor_pair.on_for_degrees(
                steering=Steering.LEFT_ON_SPOT.value, 
                speed=SpeedRPM(self._steering_correction_speed_rpm), 
                degrees=self._steering_correction_motor_degrees
            )
            self._last_time_left_corrected = True
        elif not self._last_time_right_corrected and self._should_correct_to_right() :
            self._logger.debug('Correcting to right')
            self._motor_pair.on_for_degrees(
                steering=Steering.RIGHT_ON_SPOT.value, 
                speed=SpeedRPM(self._steering_correction_speed_rpm), 
                degrees=self._steering_correction_motor_degrees
            )
            self._last_time_right_corrected = True
        else:
            self._last_time_right_corrected = False
            self._last_time_left_corrected = False

    def move_forward(self, no_of_squares: int = 1):
        self._logger.debug('Move_forward')
        time.sleep(0.1)
        _distances = self._distance_sensors.get_distances()
        self._logger.debug('Distances before: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        _angle_before = self._gyro.get_orientation()
        _speed = SpeedRPM(self._move_forward_speed_percent * self._move_forward_speed_factor)
        _move_time_sec = self._get_move_square_forward_time_sec(
            front_distance_mm = _distances['front'] * 10, 
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
        time.sleep(0.1)
        _distances = self._distance_sensors.get_distances()
        self._logger.debug('Distances after move before correction: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        self._correct_after_move_forward()
        _front_distance = self._distance_sensors.get_distances()['front']
        if _front_distance < 6.0 and _front_distance > 3.0:
            _distance_to_compensate_mm = (_front_distance - 3.0) * 10
            if _distance_to_compensate_mm > 5.0:
                self._logger.debug('Need to correct front distance for {} mm'.format(_distance_to_compensate_mm))
                self._motor_pair.on_for_rotations(
                    steering=Steering.STRAIGHT.value, 
                    speed=SpeedRPM(self._steering_correction_speed_rpm * self._move_forward_speed_factor), 
                    rotations=(_distance_to_compensate_mm / self._wheel_circumference_mm),
                    brake=True, block=True
                )
        _front_distance_remainder = _distances['front'] % 18
        self._logger.debug('Front distance remainder={}'.format(_front_distance_remainder))
        if _distances['front'] < 3 * 18 and _front_distance_remainder > 4.5 and _front_distance_remainder < 16.5:
            self._logger.debug('Bad front distance remainder. I may be at bad angle')
        self._logger.debug('Move_forward done')

    def turn_left(self):
        self._logger.debug('turn_left')
        _power_current = self._power_supply.measured_amps
        _power_voltage = self._power_supply.measured_volts
        self._logger.debug('Power current={}, voltage={}'.format(_power_current, _power_voltage))
        _angle_before = self._gyro.get_orientation()
        time.sleep(0.1)
        _distances = self._distance_sensors.get_distances()
        self._logger.debug('Distances before: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        _compensating_factor = 4.0
        self._logger.debug('Compensating factor={}'.format(_compensating_factor))
        self._motor_pair.on_for_degrees(
            steering = Steering.LEFT_ON_SPOT.value, 
            speed = SpeedRPM(self._turn_speed_percent), 
            degrees = self._motor_degrees_for_90_degree_turn + _compensating_factor, 
            brake=True, block=True
        )
        self._last_time_right_corrected = False
        self._last_time_left_corrected = False
        _angle_after = self._gyro.get_orientation()
        self._logger.debug('Gyro angle change={}'.format(_angle_after - _angle_before))
        time.sleep(0.1)
        _distances = self._distance_sensors.get_distances()
        self._logger.debug('Distances after: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        _front_distance_remainder = _distances['front'] % 18
        self._logger.debug('Front distance remainder={}'.format(_front_distance_remainder))
        if _distances['front'] < 3 * 18 and _front_distance_remainder > 4.5 and _front_distance_remainder < 16.5:
            self._logger.debug('Bad front distance remainder. I may be at bad angle')
        self._logger.debug('turn_left done')

    def turn_right(self):
        self._logger.debug('turn_right')
        _power_current = self._power_supply.measured_amps
        _power_voltage = self._power_supply.measured_volts
        self._logger.debug('Power current={}, voltage={}'.format(_power_current, _power_voltage))
        _angle_before = self._gyro.get_orientation()
        time.sleep(0.1)
        _distances = self._distance_sensors.get_distances()
        self._logger.debug('Distances before: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        _compensating_factor = 1.0
        self._logger.debug('Compensating factor={}'.format(_compensating_factor))
        self._motor_pair.on_for_degrees(
            steering = Steering.RIGHT_ON_SPOT.value, 
            speed = SpeedRPM(self._turn_speed_percent), 
            degrees = self._motor_degrees_for_90_degree_turn + _compensating_factor, 
            brake=True, block=True
        )
        self._last_time_right_corrected = False
        self._last_time_left_corrected = False
        _angle_after = self._gyro.get_orientation()
        self._logger.debug('Gyro angle change={}'.format(_angle_after - _angle_before))
        time.sleep(0.1)
        _distances = self._distance_sensors.get_distances()
        self._logger.debug('Distances after: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        _front_distance_remainder = _distances['front'] % 18
        self._logger.debug('Front distance remainder={}'.format(_front_distance_remainder))
        if _distances['front'] < 3 * 18 and _front_distance_remainder > 4.5 and _front_distance_remainder < 16.5:
            self._logger.debug('Bad front distance remainder. I may be at bad angle')
        self._logger.debug('turn_right done')

    def turn_back(self):
        self._logger.debug('turn_back')
        _power_current = self._power_supply.measured_amps
        _power_voltage = self._power_supply.measured_volts
        self._logger.debug('Power current={}, voltage={}'.format(_power_current, _power_voltage))
        _angle_before = self._gyro.get_orientation()
        time.sleep(0.1)
        _distances = self._distance_sensors.get_distances()
        self._logger.debug('Distances before: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
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
        self._last_time_right_corrected = False
        self._last_time_left_corrected = False
        _angle_after = self._gyro.get_orientation()
        self._logger.debug('Gyro angle change={}'.format(_angle_after - _angle_before))
        time.sleep(0.1)
        _distances = self._distance_sensors.get_distances()
        self._logger.debug('Distances after: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        _front_distance_remainder = _distances['front'] % 18
        self._logger.debug('Front distance remainder={}'.format(_front_distance_remainder))
        if _distances['front'] < 3 * 18 and _front_distance_remainder > 4.5 and _front_distance_remainder < 16.5:
            self._logger.debug('Bad front distance remainder. I may be at bad angle')
        self._logger.debug('turn_back done')

    def no_turn(self):
        pass
