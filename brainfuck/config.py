from dataclasses import dataclass
from typing import Final

from exeptions import ExecutionError

__all__ = [
    "Config",
]


@dataclass
class Config:
    """
    A class that contains all the run parameters and some useful
    functions related to the parameters.
    """

    # length of the values tape
    TAPE_LEN: Final[int] = 30_000
    # whether the tape is looped or not (if it is, when the pointer is
    # moved beyond one of its ends, it moves to the other end)
    IS_LOOPED: Final[bool] = True

    # number of cell variants (for maximum value `cls.maximum` is used);
    # made to emulate C language
    MAX_NUMBER: Final[int] = 256
    # signed/unsigned value;
    # if True, it simply adds MAX_NUMBER on the reverse side of zero
    # (i.e., the value of the variants doubles);
    # to get the minimum value, `cls.minimum` is used
    HAS_MINUS: Final[bool] = False
    # whether the overflow is enabled or not;
    # if it is not enabled, but it happens, then an error is raised
    HAS_OVERLOAD: Final[bool] = True

    # ======

    # After class initialization, parameters cannot be changed
    __is_init: bool = False

    def __setattr__(self, key, value):
        if self.__is_init:
            raise ValueError("Nothing can be changed after initialization")
        super().__setattr__(key, value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maximum: Final[int] = self.MAX_NUMBER - 1
        self.minimum: Final[int] = -self.MAX_NUMBER if self.HAS_MINUS else 0
        self.__is_init = True

    def check_on_max_value(self, number: int) -> int:
        """
        Returns a number reduced to the cell size.
        If the number does not fit and the overflow is off, an error is
        raised.
        Checking from the top side.
        """

        if number <= self.maximum:
            return number

        if not self.HAS_OVERLOAD:
            msg = "value is greater than maximum ({value} > {maximum})".format(
                value=number,
                maximum=self.MAX_NUMBER
            )
            raise ExecutionError(msg)

        if not self.HAS_MINUS:
            return number % self.MAX_NUMBER
        return self.minimum + (number - self.MAX_NUMBER) % (self.MAX_NUMBER*2)

    def check_on_min_value(self, number: int) -> int:
        """
        Returns a number reduced to the cell size.
        If the number does not fit and the overflow is off, an error is
        raised.
        Checking from the underside.
        """
        if number >= self.minimum:
            return number

        if not self.HAS_OVERLOAD:
            msg = "value is less than minimum ({value} < {minimum})".format(
                value=number,
                minimum=self.minimum
            )
            raise ExecutionError(msg)

        if not self.HAS_MINUS:
            return number % self.MAX_NUMBER
        return self.minimum + (number - self.MAX_NUMBER) % (self.MAX_NUMBER * 2)
