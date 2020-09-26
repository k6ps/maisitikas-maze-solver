import logging
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

    def __init__(
        self, 
        motors: Motors, 
        wall_detector: WallDetector, 
        finish_detector: FinishDetector, 
        outputs: Outputs, 
        logger = None
    ):
        self._logger = logger or logging.getLogger(__name__)
        self._motors = motors
        self._wall_detector = wall_detector
        self._finish_detector = finish_detector
        self._outputs = outputs
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

    def next_move(self) -> bool:
        self._logger.debug('Starting move')

        if self._finish_detector.is_finish():
            self._logger.info('Finised successfully in finish square!')
            self._outputs.notify(NotificationType.INFO, 'Finised successfully in finish square!')
            return True

        _front_blocked = self._wall_detector.is_front_blocked()
        _left_blocked = self._wall_detector.is_left_blocked()
        _right_blocked = self._wall_detector.is_right_blocked()
        self._logger.debug('Left blocked={}, front blocked={}, right blocked={}'.format(_left_blocked, _front_blocked, _right_blocked))

        self.next_turn(_left_blocked, _front_blocked, _right_blocked)
        self.move_forward_to_next_square()
        self._logger.debug('Move done, ready for next')
        return False


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
