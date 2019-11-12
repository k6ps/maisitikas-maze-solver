from enum import Enum

class Direction(Enum):
    NORTH = {'x': 0, 'y': 1}
    EAST = {'x': 1, 'y': 0}
    SOUTH = {'x': 0, 'y': -1}
    WEST = {'x': -1, 'y': 0}

    def get_left_direction(self):
        if self.NORTH == self:
            return self.WEST
        elif self.EAST == self:
            return self.NORTH
        elif self.SOUTH == self:
            return self.EAST
        elif self.WEST == self:
            return self.SOUTH
        else:
            return None

    def get_right_direction(self):
        if self.NORTH == self:
            return self.EAST
        elif self.EAST == self:
            return self.SOUTH
        elif self.SOUTH == self:
            return self.WEST
        elif self.WEST == self:
            return self.NORTH
        else:
            return None

    def get_back_direction(self):
        if self.NORTH == self:
            return self.SOUTH
        elif self.EAST == self:
            return self.WEST
        elif self.SOUTH == self:
            return self.NORTH
        elif self.WEST == self:
            return self.EAST
        else:
            return None
