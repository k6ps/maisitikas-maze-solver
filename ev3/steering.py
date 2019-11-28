import enum

class Steering(enum.Enum):
    STRAIGHT = 0
    LEFT_ON_SPOT = -100
    RIGHT_ON_SPOT = 100
    