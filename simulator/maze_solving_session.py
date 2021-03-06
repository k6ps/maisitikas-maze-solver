import logging
from maze_solver.direction import Direction
from maze_solver.maze_solver import MazeSolver, NotificationType
from maze_solver.curious_maze_solver import CuriousMazeSolver
from simulator.maze import Maze, MazeSquare
from simulator.simulator import SimulatorMotors, SimulatorFinishDetector, SimulatorWallDetector, SimulatorOutputs


class MazeSolvingSession(object):

    @property
    def current_square(self) -> MazeSquare:
        return self._current_square

    @property
    def current_direction(self) -> Direction:
        return self._current_direction

    @property
    def move_count(self) -> int:
        return self._move_count

    def __init__(self, maze: Maze, maze_solver: MazeSolver, max_moves: int = 9999, logger = None):
        self._logger = logger or logging.getLogger(__name__)
        self._maze = maze
        self._maze_solver = maze_solver
        self._max_moves = max_moves
        self._current_square = self._maze.get_start_square()
        self._current_direction = Direction.NORTH
        self._move_count = 0

    def start(self) -> int:
        _finished_or_cannot_move = False
        while (not _finished_or_cannot_move) and self._move_count < self._max_moves:
            self._logger.debug('Move count={}'.format(self._move_count))
            _finished_or_cannot_move = self._maze_solver.next_move()
            self._move_count += 1
        return self._move_count


class SimulatorMazeSolvingSession(MazeSolvingSession):

    def create_simulator_maze_solver(
        self,
        prefer_non_dead_ends_weight,
        prefer_unvisited_paths_weight,
        prefer_closer_to_center_weight,
        prefer_no_turns_weight,
        center_coordinates,
    ):
        _motors = SimulatorMotors(
            move_forward_callback=self.move_forward, 
            turn_right_callback=self.turn_right, 
            turn_left_callback=self.turn_left, 
            turn_back_callback=self.turn_back, 
            no_turn_callback=self.no_turn
        )
        _wall_detector = SimulatorWallDetector(
            is_left_blocked_callback=self.is_left_blocked, 
            is_front_blocked_callback=self.is_front_blocked, 
            is_right_blocked_callback=self.is_right_blocked
        )
        _finish_detector = SimulatorFinishDetector(is_finish_callback=self.is_finish)
        _outputs = SimulatorOutputs(notify_callback=self.notify)
        return CuriousMazeSolver(
            motors=_motors, 
            wall_detector=_wall_detector, 
            finish_detector=_finish_detector, 
            outputs=_outputs,
            prefer_non_dead_ends_weight=prefer_non_dead_ends_weight,
            prefer_unvisited_paths_weight=prefer_unvisited_paths_weight,
            prefer_closer_to_center_weight=prefer_closer_to_center_weight,
            prefer_no_turns_weight=prefer_no_turns_weight,
            center_coordinates=center_coordinates
        )

    # TODO: make the parameters kwargs
    def __init__(
        self, 
        maze,
        prefer_non_dead_ends_weight: int = 10,
        prefer_unvisited_paths_weight: int = 2,
        prefer_closer_to_center_weight: int = 3,
        prefer_no_turns_weight: int = 1,
        max_moves: int = 999,
        center_coordinates: list = [8, 9],
        logger=None
    ):
        self._logger = logger or logging.getLogger(__name__)
        # These are the supposed average times it would take to move, 
        # if it was a real physical thing.
        # TODO: make these parameters
        self._FORWARD_MOTION_TIME_SECONDS = 1.1
        self._TURN_MOTION_TIME_SECONDS = 0.9
        self._BACK_TURN_MOTION_TIME_SECONDS = 1.7

        _simulator_maze_solver = self.create_simulator_maze_solver(
            prefer_non_dead_ends_weight,
            prefer_unvisited_paths_weight,
            prefer_closer_to_center_weight,
            prefer_no_turns_weight,
            center_coordinates
        )
        self._motion_time_in_seconds = 0
        super().__init__(maze, _simulator_maze_solver, max_moves=max_moves)

    def is_direction_from_current_square_blocked(self, direction: Direction) -> bool:
        if direction.value['x'] == 1:
            return not self._current_square.x_plus
        elif direction.value['x'] == -1:
            return not self._current_square.x_minus
        elif direction.value['y'] == 1:
            return not self._current_square.y_plus
        elif direction.value['y'] == -1:
            return not self._current_square.y_minus
        return True

    def move_forward(self):
        _next_x = self._current_square.x + self._current_direction.value['x']
        _next_y = self._current_square.y + self._current_direction.value['y']
        self._current_square = self._maze.get_square(x = _next_x, y = _next_y)
        self._motion_time_in_seconds += self._FORWARD_MOTION_TIME_SECONDS
        self._logger.debug('Maze solver moving to square x={}, y={}'.format(_next_x, _next_y))

    def turn_right(self):
        self._current_direction = self._current_direction.get_right_direction()
        self._motion_time_in_seconds += self._TURN_MOTION_TIME_SECONDS

    def turn_left(self):
        self._current_direction = self._current_direction.get_left_direction()
        self._motion_time_in_seconds += self._TURN_MOTION_TIME_SECONDS

    def turn_back(self):
        self._current_direction = self._current_direction.get_back_direction()
        self._motion_time_in_seconds += self._BACK_TURN_MOTION_TIME_SECONDS

    def no_turn(self):
        # Don't do anything
        pass

    def is_left_blocked(self) -> bool:
        _direction = self._current_direction.get_left_direction()
        return self.is_direction_from_current_square_blocked(_direction)
    
    def is_front_blocked(self) -> bool:
        return self.is_direction_from_current_square_blocked(self._current_direction)
    
    def is_right_blocked(self) -> bool:
        _direction = self._current_direction.get_right_direction()
        return self.is_direction_from_current_square_blocked(_direction)

    def is_finish(self) -> bool:
        return self._current_square.is_finish

    def notify(self, type: NotificationType, message: str):
        # No need to notify anything in simulation, as one can follow logs in real time.
        pass

    def start(self) -> dict:
        _move_count = super().start()
        self._logger.info('Move count={}, motion time={}, '.format(
            _move_count, 
            self._motion_time_in_seconds
        ))
        return {'move_count': _move_count, 'motion_time': self._motion_time_in_seconds}
