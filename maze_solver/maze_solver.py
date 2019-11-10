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


class FinishDetector(object):
    
    def is_finish(self) -> bool:
        return False


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
    def max_moves(self) -> int:
        return self._max_moves

    @max_moves.setter
    def max_moves(self, value: int):
        self._max_moves = value

    def __init__(self, motors: Motors, wall_detector: WallDetector, finish_detector: FinishDetector, outputs: Outputs, max_moves: int = 9999):
        self._motors = motors
        self._wall_detector = wall_detector
        self._finish_detector = finish_detector
        self._outputs = outputs
        self._max_moves = max_moves
        random.seed()

    def call_one_in_random(self, call_list):
        random.choice(call_list)()

    def next_turn(self, left_blocked: bool, front_blocked: bool, right_blocked: bool):
        pass

    def next_move(self):
        # print('DEBUG - RandomWalkerMazeSolver: starting move')

        if self._finish_detector.is_finish():
            self._outputs.notify(NotificationType.INFO, 'Finised successfully in finish square!')
            return True

        _front_blocked = self._wall_detector.is_front_blocked()
        _left_blocked = self._wall_detector.is_left_blocked()
        _right_blocked = self._wall_detector.is_right_blocked()
        # print('DEBUG - RandomWalkerMazeSolver: left blocked={}, front blocked={}, right blocked={}'.format(_left_blocked, _front_blocked, _right_blocked))

        _all_blocked_retries_left = 5
        while _front_blocked and _left_blocked and _right_blocked and _all_blocked_retries_left > 0:
            _all_blocked_retries_left -= 1
            self.call_one_in_random([self._motors.turn_left, self._motors.turn_right])
            _front_blocked = self._wall_detector.is_front_blocked()
            _left_blocked = self._wall_detector.is_left_blocked()
            _right_blocked = self._wall_detector.is_right_blocked()
        if _all_blocked_retries_left <= 0:
            # print('DEBUG - RandomWalkerMazeSolver: Cannot move, blocked from all sides!')
            self._outputs.notify(NotificationType.ERROR, 'Cannot move, blocked from all sides!')
            return True
        else:
            self.next_turn(_left_blocked, _front_blocked, _right_blocked)
            self._motors.move_forward()
        # print('DEBUG - RandomWalkerMazeSolver: Move done, ready for next')
        return False

    def start(self):
        _move_count = 0
        _finished_or_cannot_move = False
        while not _finished_or_cannot_move and _move_count < self._max_moves:
            # print('DEBUG - RandomWalkerMazeSolver: move count={}'.format(_move_count))
            _finished_or_cannot_move = self.next_move()
            _move_count += 1
        if not _finished_or_cannot_move and _move_count >= self._max_moves:
            # print('DEBUG - RandomWalkerMazeSolver: Maximum allowed move count={} reached!'.format(self._max_moves))
            self._outputs.notify(NotificationType.ERROR, 'Maximum allowed move count={} reached!'.format(self._max_moves))
        return _move_count


class RandomWalkerMazeSolver(MazeSolver):

    def next_turn(self, left_blocked: bool, front_blocked: bool, right_blocked: bool):
        if not front_blocked and left_blocked and right_blocked:
            self._motors.no_turn()
        elif front_blocked and left_blocked and not right_blocked:
            self._motors.turn_right()
        elif front_blocked and not left_blocked and right_blocked:
            self._motors.turn_left()
        elif front_blocked and not left_blocked and not right_blocked:
            self.call_one_in_random([self._motors.turn_left, self._motors.turn_right])
        elif not front_blocked and not left_blocked and right_blocked:
            self.call_one_in_random([self._motors.turn_left, self._motors.no_turn])
        elif not front_blocked and left_blocked and not right_blocked:
            self.call_one_in_random([self._motors.turn_right, self._motors.no_turn])
        elif not front_blocked and not left_blocked and not right_blocked:
            self.call_one_in_random([self._motors.turn_left, self._motors.turn_right, self._motors.no_turn])


class PathRememberingMazeSolver(MazeSolver):
    pass
