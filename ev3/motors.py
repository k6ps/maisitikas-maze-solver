import math
import time
import random
import enum
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

    def __init__(self, distance_sensors: EV3UltrasoundDistanceDetectors, gyro: Gyro):
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

    def _get_move_square_forward_time_sec(self, no_of_squares: int = 1):
        _rotations = (no_of_squares * self._maze_square_length_mm) / self._wheel_circumference_mm
        return _rotations / (self._move_forward_speed_percent / 60)

    def _should_correct_to_left(self):
        _left_too_far = self._distance_sensors.are_n_last_left_distances_between_x_and_y()
        _right_too_close = self._distance_sensors.are_n_last_right_distances_below_x()
        print('DEBUG - EV3Motors: left too far={}, right too close={}'.format(_left_too_far, _right_too_close))
        return _left_too_far or _right_too_close

    def _should_correct_to_right(self):
        _right_too_far = self._distance_sensors.are_n_last_right_distances_between_x_and_y()
        _left_too_close = self._distance_sensors.are_n_last_left_distances_below_x()
        print('DEBUG - EV3Motors: right too far={}, left too close={}'.format(_right_too_far, _left_too_close))
        return _right_too_far or _left_too_close

    def _correct_after_move_forward(self):
        if not self._last_time_left_corrected and self._should_correct_to_left():
            print('DEBUG - EV3Motors: correcting to left')
            self._motor_pair.on_for_degrees(
                steering=Steering.LEFT_ON_SPOT.value, 
                speed=SpeedRPM(self._steering_correction_speed_rpm), 
                degrees=self._steering_correction_motor_degrees
            )
            self._last_time_left_corrected = True
        elif not self._last_time_right_corrected and self._should_correct_to_right() :
            print('DEBUG - EV3Motors: correcting to right')
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
        print('DEBUG - EV3Motors: move_forward')
        _distances = self._distance_sensors.get_distances()
        print('DEBUG - EV3Motors: distances before: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        _angle_before = self._gyro.get_orientation()
        _speed = SpeedRPM(self._move_forward_speed_percent * self._move_forward_speed_factor)
        _move_time_sec = self._get_move_square_forward_time_sec(no_of_squares = no_of_squares)
        self._motor_pair.on_for_seconds(
            steering=Steering.STRAIGHT.value, 
            speed=_speed, 
            seconds=_move_time_sec,
            brake=True, block=True
        )
        _angle_after = self._gyro.get_orientation()
        print('DEBUG - EV3Motors: gyro angle change before correction={}'.format(_angle_after - _angle_before))
        _distances = self._distance_sensors.get_distances()
        print('DEBUG - EV3Motors: distances after move before correction: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        self._correct_after_move_forward()
        _front_distance = self._distance_sensors.get_distances()['front']
        if _front_distance < 6.0:
            print('DEBUG - EV3Motors: front is probably blocked, checking wether correct front distance')
            if _front_distance > 3.0:
                _distance_to_compensate_mm = (_front_distance - 3.0) * 10
                if _distance_to_compensate_mm > 5.0:
                    print('DEBUG - EV3Motors: need to correct front distance for {} mm'.format(_distance_to_compensate_mm))
                    self._motor_pair.on_for_rotations(
                        steering=Steering.STRAIGHT.value, 
                        speed=SpeedRPM(self._steering_correction_speed_rpm), 
                        rotations=(_distance_to_compensate_mm / self._wheel_circumference_mm),
                        brake=True, block=True
                    )
        print('DEBUG - EV3Motors: move_forward done')

    def turn_left(self):
        print('DEBUG - EV3Motors: turn_left')
        _power_current = self._power_supply.measured_amps
        _power_voltage = self._power_supply.measured_volts
        print('DEBUG - EV3Motors: power current={}, voltage={}'.format(_power_current, _power_voltage))
        _angle_before = self._gyro.get_orientation()
        _distances = self._distance_sensors.get_distances()
        print('DEBUG - EV3Motors: distances before: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        _compensating_factor = 8.0
        print('DEBUG - EV3Motors: gcompensating factor={}'.format(_compensating_factor))
        self._motor_pair.on_for_degrees(
            steering = Steering.LEFT_ON_SPOT.value, 
            speed = SpeedRPM(self._turn_speed_percent), 
            degrees = self._motor_degrees_for_90_degree_turn + _compensating_factor, 
            brake=True, block=True
        )
        self._last_time_right_corrected = False
        self._last_time_left_corrected = False
        _angle_after = self._gyro.get_orientation()
        print('DEBUG - EV3Motors: gyro angle change={}'.format(_angle_after - _angle_before))
        _distances = self._distance_sensors.get_distances()
        print('DEBUG - EV3Motors: distances after: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        print('DEBUG - EV3Motors: turn_left done')

    def turn_right(self):
        print('DEBUG - EV3Motors: turn_right')
        _power_current = self._power_supply.measured_amps
        _power_voltage = self._power_supply.measured_volts
        print('DEBUG - EV3Motors: power current={}, voltage={}'.format(_power_current, _power_voltage))
        _angle_before = self._gyro.get_orientation()
        _distances = self._distance_sensors.get_distances()
        print('DEBUG - EV3Motors: distances before: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        _compensating_factor = 3.5
        print('DEBUG - EV3Motors: gcompensating factor={}'.format(_compensating_factor))
        self._motor_pair.on_for_degrees(
            steering = Steering.RIGHT_ON_SPOT.value, 
            speed = SpeedRPM(self._turn_speed_percent), 
            degrees = self._motor_degrees_for_90_degree_turn + _compensating_factor, 
            brake=True, block=True
        )
        self._last_time_right_corrected = False
        self._last_time_left_corrected = False
        _angle_after = self._gyro.get_orientation()
        print('DEBUG - EV3Motors: gyro angle change={}'.format(_angle_after - _angle_before))
        _distances = self._distance_sensors.get_distances()
        print('DEBUG - EV3Motors: distances after: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        print('DEBUG - EV3Motors: turn_right done')

    def turn_back(self):
        print('DEBUG - EV3Motors: turn_back')
        _power_current = self._power_supply.measured_amps
        _power_voltage = self._power_supply.measured_volts
        print('DEBUG - EV3Motors: power current={}, voltage={}'.format(_power_current, _power_voltage))
        _angle_before = self._gyro.get_orientation()
        _distances = self._distance_sensors.get_distances()
        print('DEBUG - EV3Motors: distances before: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        self._motor_pair.on_for_degrees(
            steering = random.choice([Steering.LEFT_ON_SPOT.value, Steering.RIGHT_ON_SPOT.value]), 
            speed = SpeedRPM(self._turn_speed_percent), 
            degrees = 2 * self._motor_degrees_for_90_degree_turn, 
            brake=True, block=True
        )
        self._last_time_right_corrected = False
        self._last_time_left_corrected = False
        _angle_after = self._gyro.get_orientation()
        print('DEBUG - EV3Motors: gyro angle change={}'.format(_angle_after - _angle_before))
        _distances = self._distance_sensors.get_distances()
        print('DEBUG - EV3Motors: distances after: left={}, right={}, front={}'.format(
            _distances['left'],
            _distances['right'],
            _distances['front']
        ))
        print('DEBUG - EV3Motors: turn_back done')

    def no_turn(self):
        pass
