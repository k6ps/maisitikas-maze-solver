from enum import Enum
from maze_solver.maze import Maze, MazeSquare
from maze_solver.maze_solver import MazeSolver, NotificationType
from maze_solver.simulator import SimulatorMotors, SimulatorFinishDetector, SimulatorWallDetector, SimulatorOutputs


class Direction(Enum):
    NORTH = {'x': 0, 'y': 1}
    EAST = {'x': 1, 'y': 0}
    SOUTH = {'x': 0, 'y': -1}
    WEST = {'x': -1, 'y': 0}


class MazeSolvingSession(object):

    @property
    def current_square(self) -> MazeSquare:
        return self._current_square

    @property
    def current_direction(self) -> Direction:
        return self._current_direction

    def __init__(self, maze: Maze, maze_solver: MazeSolver):
        self._maze = maze
        self._maze_solver = maze_solver
        self._current_square = self._maze.start_square()
        self._current_direction = Direction.NORTH

    def start(self):
        self._maze_solver.start()


class SimulatorMazeSolvingSession(MazeSolvingSession):

    def create_simulator_maze_solver(self):
        _motors = SimulatorMotors(
            move_forward_callback=self.move_forward, 
            turn_right_callback=self.turn_right, 
            turn_left_callback=self.turn_left, 
            no_turn_callback=self.no_turn
        )
        _wall_detector = SimulatorWallDetector(
            is_left_blocked_callback=self.is_left_blocked, 
            is_front_blocked_callback=self.is_front_blocked, 
            is_right_blocked_callback=self.is_right_blocked
        )
        _finish_detector = SimulatorFinishDetector(is_finish_callback=self.is_finish)
        _outputs = SimulatorOutputs(notify_callback=self.notify)
        return MazeSolver(
            motors=_motors, 
            wall_detector=_wall_detector, 
            finish_detector=_finish_detector, 
            outputs=_outputs
        )

    def __init__(self, maze):
        _simulator_maze_solver = self.create_simulator_maze_solver()
        super().__init__(maze, _simulator_maze_solver)

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

    def is_direction_from_current_square_blocked(self, direction):
        if direction['x'] == 1:
            return self._current_square.x_plus
        elif direction['x'] == -1:
            return self._current_square.x_minus
        elif direction['y'] == 1:
            return self._current_square.y_plus
        elif direction['y'] == -1:
            return self._current_square.y_minus
        return True

    def move_forward(self):
        _next_x = self._current_square.x + self._current_direction.value['x']
        _next_y = self._current_square.y + self._current_direction.value['y']
        self._current_square = self._maze.get_square(x = _next_x, y = _next_y)
        print('Moving to square x={}, y={}'.format(_next_x, _next_y))

    def turn_right(self):
        self._current_direction = self.get_right_direction(self._current_direction)

    def turn_left(self):
        self._current_direction = self.get_left_direction(self._current_direction)

    def no_turn(self):
        pass

    def is_left_blocked(self) -> bool:
        _direction = self.get_left_direction(self._current_direction)
        return self.is_direction_from_current_square_blocked(_direction)
    
    def is_front_blocked(self) -> bool:
        return self.is_direction_from_current_square_blocked(self._current_direction)
    
    def is_right_blocked(self) -> bool:
        _direction = self.get_right_direction(self._current_direction)
        return self.is_direction_from_current_square_blocked(_direction)

    def is_finish(self) -> bool:
        return self._current_square.is_finish

    def notify(self, type: NotificationType, message: str):
        pass

