from enum import IntEnum, auto


class Layer(IntEnum):
    BACKGROUND = auto()
    OBSTACLE = auto()
    FLOOR = auto()
    DRAGON = auto()
    UI = auto()
