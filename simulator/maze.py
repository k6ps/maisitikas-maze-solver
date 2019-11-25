class MazeSquare(object):

    def __init__(self, x: int, y: int, x_plus: bool = False, y_plus: bool = False, x_minus: bool = False, y_minus: bool = False, is_start: bool = False, is_finish: bool = False):
        self._x = x
        self._y = y
        self._x_plus = x_plus
        self._x_minus = x_minus
        self._y_plus = y_plus
        self._y_minus = y_minus
        self._is_start = is_start
        self._is_finish = is_finish
        
    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def x_plus(self) -> bool:
        return self._x_plus

    @property
    def x_minus(self) -> bool:
        return self._x_minus

    @property
    def y_plus(self) -> bool:
        return self._y_plus

    @property
    def y_minus(self) -> bool:
        return self._y_minus
 
    @property
    def is_start(self) -> bool:
        return self._is_start

    @property
    def is_finish(self) -> bool:
        return self._is_finish


class Maze(object):

    @property
    def name(self) -> str:
        return self._name

    def get_start_square(self) -> MazeSquare:
        return self._start_square

    def get_key_for_square(self, x: int, y: int) -> str:
        return '{}-{}'.format(x, y)

    def __init__(self, squares: list, name: str = ''):
        self._squares = squares
        self._name = name
        self._squares_dict = {}
        for _square in self._squares:
            _key = self.get_key_for_square(_square.x, _square.y)
            self._squares_dict[_key] = _square
            if _square.is_start:
                self._start_square = _square
    
    def get_square(self, x: int, y: int) -> MazeSquare:
        _key = self.get_key_for_square(x, y)
        return self._squares_dict[_key]
