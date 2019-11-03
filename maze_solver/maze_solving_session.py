from maze_solver.maze import Maze, MazeSquare
from maze_solver.maze_solver import MazeSolver

class MazeSolvingSession(object):

    @property
    def current_square(self) -> MazeSquare:
        return self._current_square

    def __init__(self, maze: Maze, maze_solver: MazeSolver):
        self._maze = maze
        self._maze_solver = maze_solver
        self._current_square = self._maze.start_square()

    def start(self):
        self._maze_solver.start()
