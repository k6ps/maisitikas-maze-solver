import unittest
from simulator.maze import Maze, MazeSquare

class MazeTests(unittest.TestCase):

    def setUp(self):
        self._square_11 = MazeSquare(x = 1, y = 1)
        self._square_22 = MazeSquare(x = 2, y = 2, is_start=True)
        self._test_squares = [
            self._square_11,
            MazeSquare(x = 2, y = 1),
            MazeSquare(x = 1, y = 2),
            self._square_22,
        ]
        self._maze = Maze(self._test_squares)

    def test_shoud_find_correct_start_square(self):
        _start_square = self._maze.get_start_square()
        self.assertEqual(self._square_22, _start_square)

    def test_should_get_correct_square(self):
        _square_1_1 = self._maze.get_square(x = 1, y = 1)
        self.assertEqual(self._square_11, _square_1_1)
        
