from typing import Final


__all__ = [
    "Config",
]


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

    maximum: Final[int] = MAX_NUMBER - 1
    minimum: Final[int] = -MAX_NUMBER if HAS_MINUS else 0

    @classmethod
    def check_on_max_value(cls, number: int) -> int:
        """
        Returns a number reduced to the cell size.
        If the number does not fit and the overflow is off, an error is
        raised.
        Checking from the top side.
        """

        if number <= cls.maximum:
            return number

        if not cls.HAS_OVERLOAD:
            msg = "value is greater than maximum ({value} > {maximum})".format(
                value=number,
                maximum=cls.MAX_NUMBER
            )
            raise ValueError(msg)

        if not cls.HAS_MINUS:
            return number % cls.MAX_NUMBER
        return cls.minimum + (number - cls.MAX_NUMBER) % (cls.MAX_NUMBER*2)

    @classmethod
    def check_on_min_value(cls, number: int) -> int:
        """
        Returns a number reduced to the cell size.
        If the number does not fit and the overflow is off, an error is
        raised.
        Checking from the underside.
        """
        if number >= Config.minimum:
            return number

        if not Config.HAS_OVERLOAD:
            msg = "value is less than minimum ({value} < {minimum})".format(
                value=number,
                minimum=Config.minimum
            )
            raise ValueError(msg)

        if not cls.HAS_MINUS:
            return number % cls.MAX_NUMBER
        return cls.minimum + (number - cls.MAX_NUMBER) % (cls.MAX_NUMBER * 2)
