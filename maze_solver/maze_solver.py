import random
from enum import Enum
from maze_solver.direction import Direction

class Motors(object):

    def move_forward(self):
        pass

    def turn_right(self):
        pass

    def turn_left(self):
        pass

    def turn_back(self):
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
        pass

    def next_turn_front_and_right_unblocked(self):
        pass

    def next_turn_front_and_left_unblocked(self):
        pass

    def next_turn_all_unblocked(self):
        pass

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

    def next_turn_left_and_right_unblocked(self):
        self.call_one_in_random([self.turn_left, self.turn_right])

    def next_turn_front_and_right_unblocked(self):
        self.call_one_in_random([self.turn_right, self._motors.no_turn])

    def next_turn_front_and_left_unblocked(self):
        self.call_one_in_random([self.turn_left, self._motors.no_turn])

    def next_turn_all_unblocked(self):
        self.call_one_in_random([self.turn_left, self.turn_right, self._motors.no_turn])


class Square(object):

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def is_dead_end(self) -> bool:
        return self._is_dead_end

    @is_dead_end.setter
    def is_dead_end(self, value: bool):
        self._is_dead_end = value

    def __init__(self, x: int, y: int, is_dead_end: bool = False):
        self._x = x
        self._y = y
        self._is_dead_end = is_dead_end


# Prefers unexplored paths, remembers and avoids dead-ends - but can still 
# randomly wander in already explored areas.
class CuriousMazeSolver(RandomWalkerMazeSolver):

    @property
    def current_square(self) -> Square:
        return self._current_square

    @property
    def current_direction(self) -> Direction:
        return self._current_direction

    def get_key_for_square(self, x: int, y: int) -> str:
        return '{}-{}'.format(x, y)

    def is_visited(self, x: int, y: int) -> bool:
        return self.get_key_for_square(x, y) in self._visited_squares

    def is_dead_end(self, x: int, y: int) -> bool:
        _key = self.get_key_for_square(x, y)
        if _key not in self._visited_squares:
            return False
        else:
            return self._visited_squares[_key].is_dead_end

    def __init__(self, motors: Motors, wall_detector: WallDetector, finish_detector: FinishDetector, outputs: Outputs, max_moves: int = 9999):
        super().__init__(motors, wall_detector, finish_detector, outputs, max_moves)
        self._visited_squares = {}
        _start_square = Square(x = 1, y = 1)
        self._current_square = _start_square
        self._current_direction = Direction.NORTH
        self._last_square_was_dead_end = False

    def turn_left(self):
        super().turn_left()
        self._current_direction = self._current_direction.get_left_direction()
        print('DEBUG - CuriousMazeSolver: direction is now {}'.format(self._current_direction))

    def turn_right(self):
        super().turn_right()
        self._current_direction = self._current_direction.get_right_direction()
        print('DEBUG - CuriousMazeSolver: direction is now {}'.format(self._current_direction))

    def turn_back(self):
        super().turn_back()
        self._current_direction = self._current_direction.get_back_direction()
        print('DEBUG - CuriousMazeSolver: direction is now {}'.format(self._current_direction))

    def add_square_as_visited(self, square):
        self._visited_squares[self.get_key_for_square(square.x, square.y)] = square

    def move_forward_to_next_square(self):
        super().move_forward_to_next_square()
        self.add_square_as_visited(self._current_square)
        _new_x = self._current_square.x + self._current_direction.value['x']
        _new_y = self._current_square.y + self._current_direction.value['y']
        self._current_square = Square(x = _new_x, y = _new_y)
        print('DEBUG - CuriousMazeSolver: current square is now x={}, y={}'.format(_new_x, _new_y))

    def is_dead_end_in_direction(self, direction: Direction) -> bool:
        return self.is_dead_end(
            self._current_square.x + direction.value['x'],
            self._current_square.y + direction.value['y']
        )

    def mark_current_square_as_dead_end(self):
        self._current_square.is_dead_end = True
        self._last_square_was_dead_end = True
        print('DEBUG - CuriousMazeSolver: square is dead end!! x={}, y={}'.format(
            self._current_square.x, 
            self._current_square.y
        ))

    def is_left_dead_end(self) -> bool:
        return self.is_dead_end_in_direction(self._current_direction.get_left_direction())

    def is_right_dead_end(self) -> bool:
        return self.is_dead_end_in_direction(self._current_direction.get_right_direction())

    def is_front_dead_end(self) -> bool:
        return self.is_dead_end_in_direction(self._current_direction)

    def next_turn_none_unblocked(self):
        self.mark_current_square_as_dead_end()
        super().next_turn_none_unblocked()

    def next_turn_only_front_unblocked(self):
        if self._last_square_was_dead_end:
            self.mark_current_square_as_dead_end()
        super().next_turn_only_front_unblocked()

    def next_turn_only_right_unblocked(self):
        if self._last_square_was_dead_end:
            self.mark_current_square_as_dead_end()
        super().next_turn_only_right_unblocked()

    def next_turn_only_left_unblocked(self):
        if self._last_square_was_dead_end:
            self.mark_current_square_as_dead_end()
        super().next_turn_only_left_unblocked()

    def next_turn_left_and_right_unblocked(self):
        if not self.is_right_dead_end() and self.is_left_dead_end():
            self.turn_right()
        elif self.is_right_dead_end() and not self.is_left_dead_end():
            self.turn_left()
        else:
            self._last_square_was_dead_end = False
            super().next_turn_left_and_right_unblocked()

    def next_turn_front_and_right_unblocked(self):
        if not self.is_right_dead_end() and self.is_front_dead_end():
            self.turn_right()
        elif self.is_right_dead_end() and not self.is_front_dead_end():
            self._motors.no_turn()
        else:
            self._last_square_was_dead_end = False
            super().next_turn_front_and_right_unblocked()

    def next_turn_front_and_left_unblocked(self):
        if not self.is_left_dead_end() and self.is_front_dead_end():
            self.turn_left()
        elif self.is_left_dead_end() and not self.is_front_dead_end():
            self._motors.no_turn()
        else:
            self._last_square_was_dead_end = False
            super().next_turn_front_and_left_unblocked()

    def next_turn_all_unblocked(self):
        if not self.is_left_dead_end() and self.is_front_dead_end() and self.is_right_dead_end():
                self.turn_left()
        elif self.is_left_dead_end() and self.is_front_dead_end() and not self.is_right_dead_end():
                self.turn_right()
        elif self.is_left_dead_end() and not self.is_front_dead_end() and self.is_right_dead_end():
                self._motors.no_turn()
        else:
            self._last_square_was_dead_end = False
            super().next_turn_all_unblocked()
