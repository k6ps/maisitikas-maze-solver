from ev3dev2.motor import OUTPUT_A, OUTPUT_B, MoveSteering, MoveDifferential, SpeedPercent, SpeedRPM
from ev3dev2.wheel import EV3EducationSetTire
import math


class EV3Motors(object):

    def __init__(self):
        self._motor_pair = MoveDifferential(OUTPUT_A, OUTPUT_B, EV3EducationSetTire, 81)
        # self._motor_pair = MoveSteering(OUTPUT_A, OUTPUT_B)
        self._maze_square_length_mm = 180
        self._move_forward_speed_percent = 35
        self._move_forward_speed_factor = -1
        self._turn_speed_percent = 50
        self._wheel_diameter_mm = 56
        self._wheelbase_width_mm = 130.2

    def move_forward(self, no_of_squares: int = 1):
        _speed = self._move_forward_speed_percent * self._move_forward_speed_factor
        self._motor_pair.on_for_distance(SpeedRPM(_speed), no_of_squares * self._maze_square_length_mm)

    def turn_left(self):
        self._motor_pair.turn_left(SpeedRPM(self._turn_speed_percent), 90)
        # self._motor_pair.on_for_degrees(
        #     steering = -100, 
        #     speed = SpeedRPM(self._turn_speed_percent), 
        #     degrees = 130, 
        #     brake=True, block=False
        # )

    def turn_right(self):
        self._motor_pair.turn_right(SpeedRPM(self._turn_speed_percent), 90)
        # self._motor_pair.on_for_degrees(
        #     steering = 100, 
        #     speed = SpeedRPM(self._turn_speed_percent), 
        #     degrees = 90, 
        #     brake=True, block=False
        # )

    def turn_back(self):
        self._motor_pair.turn_right(SpeedRPM(self._turn_speed_percent), 180)
        # self._motor_pair.on_for_degrees(
        #     steering = 100, 
        #     speed = SpeedRPM(self._turn_speed_percent), 
        #     degrees = 180, 
        #     brake=True, block=False
        # )
