import random
from enum import Enum


class Motors(object):
    """
    Abstract class, please implement all methods.
    """

    def move_forward(self):
        raise NotImplementedError( "Please implement this" )

    def turn_right(self):
        raise NotImplementedError( "Please implement this" )

    def turn_left(self):
        raise NotImplementedError( "Please implement this" )

    def turn_back(self):
        raise NotImplementedError( "Please implement this" )

    def no_turn(self):
        raise NotImplementedError( "Please implement this" )


class FinishDetector(object):
    """
    Abstract class, please implement all methods.
    """

    def is_finish(self) -> bool:
        raise NotImplementedError( "Please implement this" )


class WallDetector(object):
    """
    Abstract class, please implement all methods.
    """
    
    def is_left_blocked(self) -> bool:
        raise NotImplementedError( "Please implement this" )
    
    def is_front_blocked(self) -> bool:
        raise NotImplementedError( "Please implement this" )
    
    def is_right_blocked(self) -> bool:
        raise NotImplementedError( "Please implement this" )


class NotificationType(Enum):
    INFO = 1
    ERROR = 3


class Outputs(object):
    """
    Abstract class, please implement all methods.
    """

    def notify(self, type: NotificationType, message: str):
        raise NotImplementedError( "Please implement this" )


class MazeSolver(object):
    """
    Abstract class, please implement at least the following methods:
    * next_turn_left_and_right_unblocked
    * next_turn_front_and_right_unblocked
    * next_turn_front_and_left_unblocked
    * next_turn_all_unblocked
    """

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

    def turn_right(self):
        self._motors.turn_right()

    def turn_left(self):
        self._motors.turn_left()

    def turn_back(self):
        self._motors.turn_back()

    def next_turn_none_unblocked(self):
        self.turn_back()

    def next_turn_only_front_unblocked(self):
        self._motors.no_turn()

    def next_turn_only_right_unblocked(self):
        self.turn_right()

    def next_turn_only_left_unblocked(self):
        self.turn_left()

    def next_turn_left_and_right_unblocked(self):
        raise NotImplementedError( "Please implement this" )

    def next_turn_front_and_right_unblocked(self):
        raise NotImplementedError( "Please implement this" )

    def next_turn_front_and_left_unblocked(self):
        raise NotImplementedError( "Please implement this" )

    def next_turn_all_unblocked(self):
        raise NotImplementedError( "Please implement this" )

    def next_turn(self, left_blocked: bool, front_blocked: bool, right_blocked: bool):
        if front_blocked and left_blocked and right_blocked:
            self.next_turn_none_unblocked()
        elif not front_blocked and left_blocked and right_blocked:
            self.next_turn_only_front_unblocked()
        elif front_blocked and left_blocked and not right_blocked:
            self.next_turn_only_right_unblocked()
        elif front_blocked and not left_blocked and right_blocked:
            self.next_turn_only_left_unblocked()
        elif front_blocked and not left_blocked and not right_blocked:
            self.next_turn_left_and_right_unblocked()
        elif not front_blocked and not left_blocked and right_blocked:
            self.next_turn_front_and_left_unblocked()
        elif not front_blocked and left_blocked and not right_blocked:
            self.next_turn_front_and_right_unblocked()
        elif not front_blocked and not left_blocked and not right_blocked:
            self.next_turn_all_unblocked()

    def move_forward_to_next_square(self):
        self._motors.move_forward()

    def next_move(self):
        # print('DEBUG - RandomWalkerMazeSolver: starting move')

        if self._finish_detector.is_finish():
            self._outputs.notify(NotificationType.INFO, 'Finised successfully in finish square!')
            return True

        _front_blocked = self._wall_detector.is_front_blocked()
        _left_blocked = self._wall_detector.is_left_blocked()
        _right_blocked = self._wall_detector.is_right_blocked()
        # print('DEBUG - RandomWalkerMazeSolver: left blocked={}, front blocked={}, right blocked={}'.format(_left_blocked, _front_blocked, _right_blocked))

        self.next_turn(_left_blocked, _front_blocked, _right_blocked)
        self.move_forward_to_next_square()
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
    """
    Reference implementation of MazeSolver: a maze solver that just takes random turns until
    accidentally getting to finish square. It is of course very inefficient. It takes a few
    days to solve a fairly complex 16 x 16 maze when each move or turn takes a second :)
    """

    def next_turn_left_and_right_unblocked(self):
        self.call_one_in_random([self.turn_left, self.turn_right])

    def next_turn_front_and_right_unblocked(self):
        self.call_one_in_random([self.turn_right, self._motors.no_turn])

    def next_turn_front_and_left_unblocked(self):
        self.call_one_in_random([self.turn_left, self._motors.no_turn])

    def next_turn_all_unblocked(self):
        self.call_one_in_random([self.turn_left, self.turn_right, self._motors.no_turn])
