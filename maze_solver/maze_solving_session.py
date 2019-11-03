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

    def move_forward(self):
        pass

    def turn_right(self):
        pass

    def turn_left(self):
        pass

    def no_turn(self):
        pass

    def is_left_blocked(self) -> bool:
        return False
    
    def is_front_blocked(self) -> bool:
        return False
    
    def is_right_blocked(self) -> bool:
        return False

    def is_finish(self) -> bool:
        return False

    def notify(self, type: NotificationType, message: str):
        pass

