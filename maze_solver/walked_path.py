from maze_solver.square import Square
from collections import deque

class WalkedPath(object):

    def __init__(self):
        self._visited_squares = deque()

    def get_last_square(self) -> Square:
        if len(self._visited_squares) == 0:
            return None
        else:
            return self._visited_squares[-1]

    def get_square_steps_back(self, no_of_steps: int = 0) -> Square:
        return self._visited_squares[-1 - no_of_steps]

    def append(self, square: Square):
        self._visited_squares.append(square)
