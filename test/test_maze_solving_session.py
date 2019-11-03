import unittest
from unittest.mock import MagicMock
from maze_solver.maze_solving_session import MazeSolvingSession, Direction
from maze_solver.maze import MazeSquare


class MazeSolvingSessionTests(unittest.TestCase):

    def setUp(self):
        self._maze = MagicMock()
        self._maze.start_square.return_value = MazeSquare(x = 1, y = 1, is_start=True)
        self._maze_solver = MagicMock()
        self._maze_solving_session = MazeSolvingSession(maze = self._maze, maze_solver = self._maze_solver)

    def test_should_place_maze_solver_in_square_x1_y1_before_start(self):
        self.assertEqual(1, self._maze_solving_session.current_square.x)
        self.assertEqual(1, self._maze_solving_session.current_square.x)

    def test_should_place_maze_solver_facing_north_before_start(self):
        self.assertEqual(Direction.NORTH, self._maze_solving_session.current_direction)

    def test_should_call_start_on_maze_solver_when_started(self):
        self._maze_solving_session.start()
        self._maze_solver.start.assert_called()
