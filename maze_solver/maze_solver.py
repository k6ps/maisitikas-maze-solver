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

    @current_square.setter
    def current_square(self, value: Square):
        self._current_square = value

    @property
    def current_direction(self) -> Direction:
        return self._current_direction

    @current_direction.setter
    def current_direction(self, value: Direction):
        self._current_direction = value

    @property
    def prefer_non_dead_ends_weight(self) -> int:
        return self._prefer_non_dead_ends_weight

    @prefer_non_dead_ends_weight.setter
    def prefer_non_dead_ends_weight(self, value: int):
        self._prefer_non_dead_ends_weight = value

    @property
    def prefer_unvisited_paths_weight(self) -> int:
        return self._prefer_unvisited_paths_weight

    @prefer_unvisited_paths_weight.setter
    def prefer_unvisited_paths_weight(self, value: int):
        self._prefer_unvisited_paths_weight = value

    @property
    def prefer_closer_to_center_weight(self) -> int:
        return self._prefer_closer_to_center_weight

    @prefer_closer_to_center_weight.setter
    def prefer_closer_to_center_weight(self, value: int):
        self._prefer_closer_to_center_weight = value

    @property
    def prefer_no_turns_weight(self) -> int:
        return self._prefer_no_turns_weight

    @prefer_no_turns_weight.setter
    def prefer_no_turns_weight(self, value: int):
        self._prefer_no_turns_weight = value

    @property
    def center_coordinates(self) -> list:
        return self._center_coordinates

    @center_coordinates.setter
    def center_coordinates(self, value: list):
        self._center_coordinates = value

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

    def reset_to_start_and_forget_everything(self):
        self._visited_squares = {}
        _start_square = Square(x = 1, y = 1)
        self._current_square = _start_square
        self._current_direction = Direction.NORTH
        self._last_square_was_dead_end = False

    def __init__(
        self, 
        motors: Motors, 
        wall_detector: WallDetector, 
        finish_detector: FinishDetector, 
        outputs: Outputs, 
        prefer_non_dead_ends_weight: int = 10,
        prefer_unvisited_paths_weight: int = 2,
        prefer_closer_to_center_weight: int = 3,
        prefer_no_turns_weight: int = 1,
        max_moves: int = 9999,
        center_coordinates: list = [8, 9]
    ):
        super().__init__(motors, wall_detector, finish_detector, outputs, max_moves)
        self.reset_to_start_and_forget_everything()
        self._prefer_non_dead_ends_weight = prefer_non_dead_ends_weight
        self._prefer_unvisited_paths_weight = prefer_unvisited_paths_weight
        self._prefer_closer_to_center_weight = prefer_closer_to_center_weight
        self._prefer_no_turns_weight = prefer_no_turns_weight
        self._center_coordinates = center_coordinates

    def turn_left(self):
        super().turn_left()
        self._current_direction = self._current_direction.get_left_direction()
        # print('DEBUG - CuriousMazeSolver: direction is now {}'.format(self._current_direction))

    def turn_right(self):
        super().turn_right()
        self._current_direction = self._current_direction.get_right_direction()
        # print('DEBUG - CuriousMazeSolver: direction is now {}'.format(self._current_direction))

    def turn_back(self):
        super().turn_back()
        self._current_direction = self._current_direction.get_back_direction()
        # print('DEBUG - CuriousMazeSolver: direction is now {}'.format(self._current_direction))

    def add_square_as_visited(self, square):
        self._visited_squares[self.get_key_for_square(square.x, square.y)] = square

    def move_forward_to_next_square(self):
        super().move_forward_to_next_square()
        self.add_square_as_visited(self._current_square)
        _new_x = self._current_square.x + self._current_direction.value['x']
        _new_y = self._current_square.y + self._current_direction.value['y']
        self._current_square = Square(x = _new_x, y = _new_y)
        # print('DEBUG - CuriousMazeSolver: current square is now x={}, y={}'.format(_new_x, _new_y))

    def is_dead_end_in_direction(self, direction: Direction) -> bool:
        return self.is_dead_end(
            self._current_square.x + direction.value['x'],
            self._current_square.y + direction.value['y']
        )

    def is_visited_in_direction(self, direction: Direction) -> bool:
        return self.is_visited(
            self._current_square.x + direction.value['x'],
            self._current_square.y + direction.value['y']
        )

    def mark_current_square_as_dead_end(self):
        self._current_square.is_dead_end = True
        self._last_square_was_dead_end = True
        # print('DEBUG - CuriousMazeSolver: Square is dead end! x={}, y={} !!'.format(
        #     self._current_square.x, 
        #     self._current_square.y
        # ))

    def is_left_dead_end(self) -> bool:
        return self.is_dead_end_in_direction(self._current_direction.get_left_direction())

    def is_right_dead_end(self) -> bool:
        return self.is_dead_end_in_direction(self._current_direction.get_right_direction())

    def is_front_dead_end(self) -> bool:
        return self.is_dead_end_in_direction(self._current_direction)

    def is_left_visited(self) -> bool:
        return self.is_visited_in_direction(self._current_direction.get_left_direction())

    def is_right_visited(self) -> bool:
        return self.is_visited_in_direction(self._current_direction.get_right_direction())

    def is_front_visited(self) -> bool:
        return self.is_visited_in_direction(self._current_direction)

    def get_distance_from_center(self, x: int, y: int) -> int:
        def _get_min_distance(x_or_y: int):
            _distances = []
            for coordinate in self._center_coordinates:
                _distances.append(abs(x_or_y - coordinate))
            return min(_distances)

        _min_x = _get_min_distance(x)
        _min_y = _get_min_distance(y)
        return max(_min_x, _min_y)

    def get_distance_from_center_in_direction(self, direction: Direction) -> int:
        return self.get_distance_from_center(
            self._current_square.x + direction.value['x'],
            self._current_square.y + direction.value['y']
        )

    def get_distance_from_center_in_left(self) -> int:
        return self.get_distance_from_center_in_direction(self._current_direction.get_left_direction())

    def get_distance_from_center_in_right(self) -> int:
        return self.get_distance_from_center_in_direction(self._current_direction.get_right_direction())

    def get_distance_from_center_in_front(self) -> int:
        return self.get_distance_from_center_in_direction(self._current_direction)

    def get_score_left(self) -> int:
        _no_dead_end_score = self._prefer_non_dead_ends_weight if not self.is_left_dead_end() else 0
        _unvisited_score = self._prefer_unvisited_paths_weight if not self.is_left_visited() else 0
        _closeness_to_center = 8 - self.get_distance_from_center_in_left()
        _closeness_to_center_score = self._prefer_closer_to_center_weight * (_closeness_to_center / 8)
        _no_turns_score = 0
        return _no_dead_end_score + _unvisited_score + _closeness_to_center_score + _no_turns_score

    def get_score_right(self) -> int:
        _no_dead_end_score = self._prefer_non_dead_ends_weight if not self.is_right_dead_end() else 0
        _unvisited_score = self._prefer_unvisited_paths_weight if not self.is_right_visited() else 0
        _closeness_to_center = 8 - self.get_distance_from_center_in_right()
        _closeness_to_center_score = self._prefer_closer_to_center_weight * (_closeness_to_center / 8)
        _no_turns_score = 0
        return _no_dead_end_score + _unvisited_score + _closeness_to_center_score + _no_turns_score

    def get_score_front(self) -> int:
        _no_dead_end_score = self._prefer_non_dead_ends_weight if not self.is_front_dead_end() else 0
        _unvisited_score = self._prefer_unvisited_paths_weight if not self.is_front_visited() else 0
        _closeness_to_center = 8 - self.get_distance_from_center_in_front()
        _closeness_to_center_score = self._prefer_closer_to_center_weight * (_closeness_to_center / 8)
        _no_turns_score = self._prefer_no_turns_weight
        return _no_dead_end_score + _unvisited_score + _closeness_to_center_score + _no_turns_score

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

    def next_turn_based_on_scores_between_left_and_right(self):
        _left_score = self.get_score_left()
        _right_score = self.get_score_right()
        if _left_score > _right_score:
            super().next_turn_only_left_unblocked()
        elif _left_score < _right_score:
            super().next_turn_only_right_unblocked()
        else:
            super().next_turn_left_and_right_unblocked()

    def next_turn_based_on_scores_between_front_and_right(self):
        _front_score = self.get_score_front()
        _right_score = self.get_score_right()
        if _front_score > _right_score:
            super().next_turn_only_front_unblocked()
        elif _front_score < _right_score:
            super().next_turn_only_right_unblocked()
        else:
            super().next_turn_front_and_right_unblocked()

    def next_turn_based_on_scores_between_front_and_left(self):
        # print('DEBUG - CuriousMazeSolver: next_turn_based_on_scores_between_front_and_left')
        _front_score = self.get_score_front()
        # print('DEBUG - CuriousMazeSolver: front_score={}'.format(_front_score))
        _left_score = self.get_score_left()
        # print('DEBUG - CuriousMazeSolver: left_score={}'.format(_left_score))
        if _front_score > _left_score:
            super().next_turn_only_front_unblocked()
        elif _front_score < _left_score:
            super().next_turn_only_left_unblocked()
        else:
            super().next_turn_front_and_left_unblocked()

    def next_turn_based_on_scores_between_all_directions(self):
        _front_score = self.get_score_front()
        _left_score = self.get_score_left()
        _right_score = self.get_score_right()
        if _front_score > _right_score and _front_score > _left_score:
            super().next_turn_only_front_unblocked()
        elif _left_score > _right_score and _left_score > _front_score:
            super().next_turn_only_left_unblocked()
        elif _right_score > _left_score and _right_score > _front_score:
            super().next_turn_only_right_unblocked()
        elif _front_score == _left_score and _front_score > _right_score:
            super().next_turn_front_and_left_unblocked()
        elif _left_score == _right_score and _left_score > _front_score:
            super().next_turn_left_and_right_unblocked()
        elif _front_score == _right_score and _front_score > _left_score:
            super().next_turn_front_and_right_unblocked()
        else:
            super().next_turn_all_unblocked()

    def next_turn_left_and_right_unblocked(self):
        if not self.is_right_dead_end() and self.is_left_dead_end():
            self.next_turn_only_right_unblocked()
        elif self.is_right_dead_end() and not self.is_left_dead_end():
            self.next_turn_only_left_unblocked()
        else:
            self._last_square_was_dead_end = False
            self.next_turn_based_on_scores_between_left_and_right()

    def next_turn_front_and_right_unblocked(self):
        if not self.is_right_dead_end() and self.is_front_dead_end():
            self.next_turn_only_right_unblocked()
        elif self.is_right_dead_end() and not self.is_front_dead_end():
            self.next_turn_only_front_unblocked()
        else:
            self._last_square_was_dead_end = False
            self.next_turn_based_on_scores_between_front_and_right()

    def next_turn_front_and_left_unblocked(self):
        # print('DEBUG - CuriousMazeSolver: next_turn_front_and_left_unblocked')
        if not self.is_left_dead_end() and self.is_front_dead_end():
            self.next_turn_only_left_unblocked()
        elif self.is_left_dead_end() and not self.is_front_dead_end():
            self.next_turn_only_front_unblocked()
        else:
            self._last_square_was_dead_end = False
            self.next_turn_based_on_scores_between_front_and_left()

    def next_turn_all_unblocked(self):
        # print('DEBUG - CuriousMazeSolver: ALL directions are unblocked')
        if not self.is_left_dead_end() and self.is_front_dead_end() and self.is_right_dead_end():
            # print('DEBUG - CuriousMazeSolver: front and right are dead ends')
            self.next_turn_only_left_unblocked()
        elif self.is_left_dead_end() and self.is_front_dead_end() and not self.is_right_dead_end():
            # print('DEBUG - CuriousMazeSolver: front and left are dead ends')
            self.next_turn_only_right_unblocked()
        elif self.is_left_dead_end() and not self.is_front_dead_end() and self.is_right_dead_end():
            # print('DEBUG - CuriousMazeSolver: right and left are dead ends')
            self.next_turn_only_front_unblocked()
        elif self.is_left_dead_end() and not self.is_front_dead_end() and not self.is_right_dead_end():
            # print('DEBUG - CuriousMazeSolver: left is dead end')
            self._last_square_was_dead_end = False
            self.next_turn_based_on_scores_between_front_and_right()
        elif not self.is_left_dead_end() and self.is_front_dead_end() and not self.is_right_dead_end():
            # print('DEBUG - CuriousMazeSolver: front is dead end')
            self._last_square_was_dead_end = False
            self.next_turn_based_on_scores_between_left_and_right()
        elif not self.is_left_dead_end() and not self.is_front_dead_end() and self.is_right_dead_end():
            # print('DEBUG - CuriousMazeSolver: right is dead end')
            self._last_square_was_dead_end = False
            self.next_turn_based_on_scores_between_front_and_left()
        else:
            self._last_square_was_dead_end = False
            # print('DEBUG - CuriousMazeSolver: none are dead ends')
            self.next_turn_based_on_scores_between_all_directions()
