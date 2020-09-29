class Square(object):

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def is_dead_end(self) -> bool:
        return self._is_dead_end

    @is_dead_end.setter
    def is_dead_end(self, value: bool):
        self._is_dead_end = value

    def __init__(self, x: int, y: int, is_dead_end: bool = False):
        self._x = x
        self._y = y
        self._is_dead_end = is_dead_end
        