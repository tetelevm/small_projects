
__all__ = [
    "ExecutionError",
]


class ExecutionError(ValueError):
    """
    An error occurred during program execution (controllable; a problem
    in the logic of a given program).
    """
