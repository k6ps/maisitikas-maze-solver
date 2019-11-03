import unittest
from maze_solver.maze import Maze, MazeSquare

class MazeTests(unittest.TestCase):

    def test_shoud_find_correct_start_square(self):
        _test_squares = [
            MazeSquare(x = 1, y = 1),
            MazeSquare(x = 2, y = 1),
            MazeSquare(x = 1, y = 2),
            MazeSquare(x = 2, y = 2, is_start=True),
        ]
        _maze = Maze(_test_squares)
        _start_square = _maze.start_square
        self.assertTrue(2, _start_square.x)
        self.assertTrue(2, _start_square.y)
