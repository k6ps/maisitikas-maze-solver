class Maze(object):

    @property
    def start_square(self) -> dict:
        return self._start_square

    def __init__(self):
        self._squares = []
        self._start_square = {'x': 1, 'y': 1}

    

    