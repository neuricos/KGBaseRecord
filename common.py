from enum import Enum

class OptionDiffLevel(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2

    def __ge__(self, other):
        return self.value > other.value