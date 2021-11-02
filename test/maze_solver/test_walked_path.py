import unittest
from maze_solver.walked_path import WalkedPath
from maze_solver.square import Square


class WalkedPathTest(unittest.TestCase):

    def setUp(self):
        self._walked_path = WalkedPath()

    def test_should_return_none_if_no_steps_have_been_added(self):
        self.assertIsNone(self._walked_path.get_last_square())

    def test_should_return_last_added_square_when_one_square_added(self):
        self._walked_path.append(Square(x=11, y=12))
        _actual_last_square = self._walked_path.get_last_square()
        self.assertEquals(_actual_last_square.x, 11)
        self.assertEquals(_actual_last_square.y, 12)

    def test_should_return_last_added_square_when_multiple_squares_added(self):
        self._walked_path.append(Square(x=11, y=12))
        self._walked_path.append(Square(x=12, y=13))
        self._walked_path.append(Square(x=13, y=14))
        _actual_last_square = self._walked_path.get_last_square()
        self.assertEquals(_actual_last_square.x, 13)
        self.assertEquals(_actual_last_square.y, 14)

    def test_should_return_previous_to_last_added_square_when_one_step_back_called(self):
        self._walked_path.append(Square(x=11, y=12))
        self._walked_path.append(Square(x=12, y=13))
        self._walked_path.append(Square(x=13, y=14))
        _actual_last_square = self._walked_path.get_square_steps_back(1)
        self.assertEquals(_actual_last_square.x, 12)
        self.assertEquals(_actual_last_square.y, 13)

    def test_should_return_correct_square_when_four_step_back_called(self):
        self._walked_path.append(Square(x=10, y=12))
        self._walked_path.append(Square(x=11, y=12))
        self._walked_path.append(Square(x=12, y=13))
        self._walked_path.append(Square(x=13, y=14))
        self._walked_path.append(Square(x=14, y=15))
        self._walked_path.append(Square(x=15, y=16))
        _actual_last_square = self._walked_path.get_square_steps_back(4)
        self.assertEquals(_actual_last_square.x, 11)
        self.assertEquals(_actual_last_square.y, 12)
