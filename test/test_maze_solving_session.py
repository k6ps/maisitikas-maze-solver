import unittest
from unittest.mock import MagicMock
from maze_solver.maze_solving_session import MazeSolvingSession


class MazeSolvingSessionTests(unittest.TestCase):

    def test_should_place_maze_solver_in_square_x1_y1_before_start(self):
        _maze = MagicMock()
        _maze.start_square.return_value = {'x': 1, 'y': 1}
        _maze_solver = MagicMock()
        _maze_solving_session = MazeSolvingSession(maze = _maze, maze_solver = _maze_solver)
        self.assertEqual({'x': 1, 'y': 1}, _maze_solving_session.current_square)