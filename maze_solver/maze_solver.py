import random
from enum import Enum

class Motors(object):

    def move_forward(self):
        pass

    def turn_right(self):
        pass

    def turn_left(self):
        pass

    def no_turn(self):
        pass


class WallDetector(object):
    
    def is_left_blocked(self) -> bool:
        return False
    
    def is_front_blocked(self) -> bool:
        return False
    
    def is_right_blocked(self) -> bool:
        return False


class NotificationType(Enum):
    INFO = 1
    ERROR = 3


class Outputs(object):

    def notify(self, type: NotificationType, message: str):
        pass


class MazeSolver(object):
    
    @property
    def moves_left(self) -> int:
        return self._moves_left

    @moves_left.setter
    def moves_left(self, value: int):
        self._moves_left = value

    def __init__(self, motors: Motors, wall_detector: WallDetector, outputs: Outputs, max_moves: int = 99):
        self._motors = motors
        self._wall_detector = wall_detector
        self._outputs = outputs
        self._moves_left = max_moves
        random.seed()

    def next_move(self):

        def _call_one_in_random(call_list):
            random.choice(call_list)()

        def _turn_randomly_left_or_right():
            _choice = random.randint(0, 1)
            if _choice == 0:
                self._motors.turn_left()
            else:
                self._motors.turn_right()

        _front_blocked = self._wall_detector.is_front_blocked()
        _left_blocked = self._wall_detector.is_left_blocked()
        _right_blocked = self._wall_detector.is_right_blocked()
        _all_blocked_retries_left = 5
        while _front_blocked and _left_blocked and _right_blocked and _all_blocked_retries_left > 0:
            _all_blocked_retries_left -= 1
            _call_one_in_random([self._motors.turn_left, self._motors.turn_right])
            _front_blocked = self._wall_detector.is_front_blocked()
            _left_blocked = self._wall_detector.is_left_blocked()
            _right_blocked = self._wall_detector.is_right_blocked()
        if _all_blocked_retries_left <= 0:
            raise Exception('Cannot move, blocked from all sides!')
        else:
            if not _front_blocked and _left_blocked and _right_blocked:
                self._motors.no_turn()
                self._motors.move_forward()
            elif _front_blocked and _left_blocked and not _right_blocked:
                self._motors.turn_right()
                self._motors.move_forward()
            elif _front_blocked and not _left_blocked and _right_blocked:
                self._motors.turn_left()
                self._motors.move_forward()
            elif _front_blocked and not _left_blocked and not _right_blocked:
                _call_one_in_random([self._motors.turn_left, self._motors.turn_right])
                self._motors.move_forward()
            elif not _front_blocked and not _left_blocked and _right_blocked:
                _call_one_in_random([self._motors.turn_left, self._motors.no_turn])
                self._motors.move_forward()
            elif not _front_blocked and _left_blocked and not _right_blocked:
                _call_one_in_random([self._motors.turn_right, self._motors.no_turn])
                self._motors.move_forward()
            elif not _front_blocked and not _left_blocked and not _right_blocked:
                _call_one_in_random([self._motors.turn_left, self._motors.turn_right, self._motors.no_turn])
                self._motors.move_forward()
            else:
                raise Exception('Some weird situation, i dont know what to do!')

