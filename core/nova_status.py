from enum import Enum


class Status(Enum):
    InDevelopment = 1
    ReadyForRelease = 2
    Done = 3
    Undefined = 4

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()