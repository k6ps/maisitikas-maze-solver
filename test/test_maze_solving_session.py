import unittest
from unittest.mock import MagicMock
from maze_solver.maze_solving_session import MazeSolvingSession


class MazeSolvingSessionTests(unittest.TestCase):

    def setUp(self):
        self._maze = MagicMock()
        self._maze.start_square.return_value = {'x': 1, 'y': 1}
        self._maze_solver = MagicMock()
        self._maze_solving_session = MazeSolvingSession(maze = self._maze, maze_solver = self._maze_solver)

    def test_should_place_maze_solver_in_square_x1_y1_before_start(self):
        self.assertEqual({'x': 1, 'y': 1}, self._maze_solving_session.current_square)

    def test_should_call_start_on_maze_solver_when_started(self):
        self._maze_solving_session.start()
        self._maze_solver.start.assert_called()
