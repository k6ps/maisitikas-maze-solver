import random
from enum import Enum

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

    def next_turn(self, left_blocked: bool, front_blocked: bool, right_blocked: bool):
        pass

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

    def next_turn(self, left_blocked: bool, front_blocked: bool, right_blocked: bool):
        if front_blocked and left_blocked and right_blocked:
            self.turn_back()
        elif not front_blocked and left_blocked and right_blocked:
            self._motors.no_turn()
        elif front_blocked and left_blocked and not right_blocked:
            self.turn_right()
        elif front_blocked and not left_blocked and right_blocked:
            self.turn_left()
        elif front_blocked and not left_blocked and not right_blocked:
            self.call_one_in_random([self.turn_left, self.turn_right])
        elif not front_blocked and not left_blocked and right_blocked:
            self.call_one_in_random([self.turn_left, self._motors.no_turn])
        elif not front_blocked and left_blocked and not right_blocked:
            self.call_one_in_random([self.turn_right, self._motors.no_turn])
        elif not front_blocked and not left_blocked and not right_blocked:
            self.call_one_in_random([self.turn_left, self.turn_right, self._motors.no_turn])


class Square(object):

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y


class Direction(Enum):
    NORTH = {'x': 0, 'y': 1}
    EAST = {'x': 1, 'y': 0}
    SOUTH = {'x': 0, 'y': -1}
    WEST = {'x': -1, 'y': 0}


# Prefers unexplored paths, remembers and avoids dead-ends - but can still 
# randomly wander in already explored areas.
class CuriousMazeSolver(MazeSolver):

    @property
    def current_square(self) -> Square:
        return self._current_square

    @property
    def current_direction(self) -> Direction:
        return self._current_direction

    def get_left_direction(self, front_direction):
        if Direction.NORTH == front_direction:
            return Direction.WEST
        elif Direction.EAST == front_direction:
            return Direction.NORTH
        elif Direction.SOUTH == front_direction:
            return Direction.EAST
        elif Direction.WEST == front_direction:
            return Direction.SOUTH
        else:
            return None

    def get_right_direction(self, front_direction):
        if Direction.NORTH == front_direction:
            return Direction.EAST
        elif Direction.EAST == front_direction:
            return Direction.SOUTH
        elif Direction.SOUTH == front_direction:
            return Direction.WEST
        elif Direction.WEST == front_direction:
            return Direction.NORTH
        else:
            return None

    def get_back_direction(self, front_direction):
        if Direction.NORTH == front_direction:
            return Direction.SOUTH
        elif Direction.EAST == front_direction:
            return Direction.WEST
        elif Direction.SOUTH == front_direction:
            return Direction.NORTH
        elif Direction.WEST == front_direction:
            return Direction.EAST
        else:
            return None
            
    def get_key_for_square(self, x: int, y: int) -> str:
        return '{}-{}'.format(x, y)

    def is_visited(self, x: int, y: int) -> bool:
        return self.get_key_for_square(x, y) in self._visited_squares

    def __init__(self, motors: Motors, wall_detector: WallDetector, finish_detector: FinishDetector, outputs: Outputs, max_moves: int = 9999):
        super().__init__(motors, wall_detector, finish_detector, outputs, max_moves)
        self._visited_squares = {}
        _start_square = Square(x = 1, y = 1)
        self._current_square = _start_square
        self._current_direction = Direction.NORTH

    def turn_left(self):
        super().turn_left()
        self._current_direction = self.get_left_direction(self._current_direction)
        print('DEBUG - CuriousMazeSolver: direction is now {}'.format(self._current_direction))

    def turn_right(self):
        super().turn_right()
        self._current_direction = self.get_right_direction(self._current_direction)
        print('DEBUG - CuriousMazeSolver: direction is now {}'.format(self._current_direction))

    def turn_back(self):
        super().turn_back()
        self._current_direction = self.get_back_direction(self._current_direction)
        print('DEBUG - CuriousMazeSolver: direction is now {}'.format(self._current_direction))

    def move_forward_to_next_square(self):
        super().move_forward_to_next_square()
        self._visited_squares[self.get_key_for_square(self._current_square.x, self._current_square.y)] = self._current_square
        _new_x = self._current_square.x + self._current_direction.value['x']
        _new_y = self._current_square.y + self._current_direction.value['y']
        self._current_square = Square(x = _new_x, y = _new_y)
        print('DEBUG - CuriousMazeSolver: current square is now x={}, y={}'.format(_new_x, _new_y))

    def next_turn(self, left_blocked: bool, front_blocked: bool, right_blocked: bool):
        if front_blocked and left_blocked and right_blocked:
            self.turn_back()
        elif not front_blocked and left_blocked and right_blocked:
            self._motors.no_turn()
        elif front_blocked and left_blocked and not right_blocked:
            self.turn_right()
        elif front_blocked and not left_blocked and right_blocked:
            self.turn_left()
        elif front_blocked and not left_blocked and not right_blocked:
            random_int = random.randint(1,2)
            if random_int == 1:
                self.turn_left()
            elif random_int == 2:
                self.turn_right()
        elif not front_blocked and not left_blocked and right_blocked:
            random_int = random.randint(1,2)
            if random_int == 1:
                self.turn_left()
            # elif random_int == 2:
            #     self._motors.no_turn()
        elif not front_blocked and left_blocked and not right_blocked:
            random_int = random.randint(1,2)
            if random_int == 1:
                self.turn_right()
            # elif random_int == 2:
            #     self._motors.no_turn()
        elif not front_blocked and not left_blocked and not right_blocked:
            random_int = random.randint(1,3)
            if random_int == 1:
                self.turn_left()
            elif random_int == 2:
                self.turn_right()
            # elif random_int == 3:
            #     self._motors.no_turn()
        
