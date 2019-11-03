from maze_solver.maze import Maze
from maze_solver.maze_solver import MazeSolver

class MazeSolvingSession(object):

    @property
    def current_square(self) -> dict:
        return self._current_square

    def __init__(self, maze: Maze, maze_solver: MazeSolver):
        self._maze = maze
        self._maze_solver = maze_solver
        self._current_square = self._maze.start_square()
        print("start square = ")
        print(self._maze.start_square())