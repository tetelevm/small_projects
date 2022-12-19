from abc import ABC, abstractmethod
from typing import Protocol

from config import Config


__all__ = [
    "Operator",
    "End",

    "Right",
    "Left",
    "Increment",
    "Decrement",
    "Output",
    "Input",
    "While",
    "WhileEnd",

    "GiveSomeFishfood",
    "Repeat",
    "GiveBanana",
]


# === system classes ===================================================


class _Runtime(Protocol):
    """
    Runtime interface. Similar to the `Runtime` class.
    """

    tape: list[int]
    pointer: int
    cursor: int
    is_running: bool
    operators: list

    _linebreak_required: bool


class Operator(ABC):
    """
    Operator base class.
    The main method of the class is `do`, it contains all the logic for
    changing the timing.
    Contains name and position to output program errors.
    """

    error_info: tuple[str, str]

    def __init__(self, name: str, error_info: tuple[str, str]):
        self.name = name
        self.error_info = error_info

    @abstractmethod
    def do(self, runtime: _Runtime):
        pass


class End(Operator):
    """
    End of program operator.
    Not included in languages (usually), it is used mainly as a system
    operator - added to the end of the program to finish it.
    """

    def do(self, runtime):
        runtime.is_running = False


# === original operators ===============================================


class Right(Operator):
    """
    Moves the tape pointer to the right.
    If the cell was the last one, it moves to the first one if the tape
    is looped, else it triggers an error.
    """

    def do(self, runtime):
        runtime.pointer += 1
        if runtime.pointer >= Config.TAPE_LEN:
            if Config.IS_LOOPED:
                runtime.pointer = 0
            else:
                msg = "tape pointer out of range ({pointer} > {size})".format(
                    pointer=runtime.pointer,
                    size=Config.TAPE_LEN - 1
                )
                raise ValueError(msg)


class Left(Operator):
    """
    Moves the pointer to the left.
    If there was the first (zero) cell, it moves the cursor to the last
    element if the tape is looped, else it generates an error.
    """

    def do(self, runtime):
        runtime.pointer -= 1
        if runtime.pointer < 0:
            if Config.IS_LOOPED:
                runtime.pointer = Config.TAPE_LEN - 1
            else:
                msg = f"tape pointer out of range ({runtime.pointer} < 0)"
                raise ValueError(msg)


class Increment(Operator):
    """
    Increases the value of the current cell by 1.
    Since the original BrainFuck was implemented in languages with
    overflow, it either executes it (if necessary) or generates an error.
    """

    def do(self, runtime):
        new_val = runtime.tape[runtime.pointer] + 1
        runtime.tape[runtime.pointer] = Config.check_on_max_value(new_val)


class Decrement(Operator):
    """
    Reduces the value of the current cell by 1.
    Since the original BrainFuck was implemented in languages with
    overflow, it either executes it (if necessary) or generates an error.
    """

    def do(self, runtime):
        runtime.tape[runtime.pointer] -= 1
        if runtime.tape[runtime.pointer] < Config.minimum:
            if Config.HAS_OVERLOAD:
                runtime.tape[runtime.pointer] = Config.maximum
            else:
                msg = "value is less than minimum ({value} < {minimum})".format(
                    value=runtime.tape[runtime.pointer],
                    minimum=Config.minimum
                )
                raise ValueError(msg)


class Output(Operator):
    """
    Outputs the current cell as a Unicode character (without line break).
    If the cell value is out of Unicode, it generates an error.
    """

    UNICODE_MAX = 0x10ffff

    @classmethod
    def is_unicode(cls, char_code: int) -> bool:
        return 0 <= char_code < cls.UNICODE_MAX

    def do(self, runtime):
        char_code = runtime.tape[runtime.pointer]
        if not self.is_unicode(char_code):
            msg = "value is out of range of unicode ({value} <> [0:{max}])".format(
                value=char_code,
                max=self.UNICODE_MAX
            )
            raise ValueError(msg)
        print(chr(char_code), end="")
        runtime._linebreak_required = char_code != 10  # not "\n"


class Input(Operator):
    """
    Reads the character and puts its code in the cell.
    If more than one character is entered, only the first character is
    used.
    """

    def do(self, runtime):
        char = input("> ")  # TODO: ctrl-c
        char = char.lstrip(" ")[:1]
        char_code = ord(char or "\n")
        runtime.tape[runtime.pointer] = Config.check_on_max_value(char_code)


class While(Operator):
    """
    The beginning of the loop.
    If the value in the current cell is NOT zero, nothing happens.
    If the value is zero, it searches for the relevant close loop
    statement and moves the cursor to it. Nesting is taken into account;
    if the end of the program is found during the search, it is stopped.
    """

    def do(self, runtime):
        if not runtime.tape[runtime.pointer]:
            nesting = 0
            while True:
                operator = runtime.operators[runtime.cursor]
                if isinstance(operator, While):
                    nesting += 1
                elif isinstance(operator, WhileEnd):
                    nesting -= 1

                if nesting == 0:
                    break
                elif isinstance(operator, End):
                    runtime.cursor -= 1
                    break

                runtime.cursor += 1


class WhileEnd(Operator):
    """
    End of cycle.
    If the value in the current cell is null, nothing happens.
    If the value is not zero, the relevant loop opening statement (at
    the back) is searched for and the cursor is moved to it. Nesting is
    taken into account; if the beginning of the program is found during
    the search, an error is called.
    """

    def do(self, runtime):
        if runtime.tape[runtime.pointer]:
            nesting = 0
            while True:
                operator = runtime.operators[runtime.cursor]
                if isinstance(operator, WhileEnd):
                    nesting += 1
                elif isinstance(operator, While):
                    nesting -= 1

                if nesting == 0:
                    break
                elif runtime.cursor == 0:
                    raise ValueError("unexpected end of loop")

                runtime.cursor -= 1


# === extended operators ===============================================


class GiveSomeFishfood(Operator):
    """
    The joking operator from the Blub language.
    """

    def do(self, runtime):
        if runtime._linebreak_required:
            print()
        print("*Fishfood transfer takes place* - \"Blub!\"")
        runtime._linebreak_required = False


class Repeat(Operator):
    """
    Repeats the previous operator.
    May not work correctly with the `While` and `WhileEnd` operators.
    It works recursively, so it may generate an error if there is too
    much nesting.
    """

    def do(self, runtime, _cursor: int = None):
        if runtime.cursor == 0 and not _cursor:
            raise ValueError("no previous operator found")

        cursor = (_cursor or runtime.cursor) - 1
        previous_operator = runtime.operators[cursor]
        if isinstance(previous_operator, Repeat):
            previous_operator.do(runtime, cursor)
        else:
            previous_operator.do(runtime)


class GiveBanana(Operator):
    """
    The joking operator from the Ook language.
    """

    def do(self, runtime):
        if runtime._linebreak_required:
            print()
        print("*Banana transfer takes place* - \"Ook!\"")
        runtime._linebreak_required = False








