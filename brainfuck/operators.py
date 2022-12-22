from abc import ABC, abstractmethod

from exeptions import ExecutionError
from program import Program


__all__ = [
    "Operator",
    "Start",
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


class Operator(ABC):
    """
    Operator base class.
    The main method of the class is `do`, it contains all the logic for
    changing the timing.
    Contains name and position to output program errors.
    """

    name: str
    position: tuple[int, int]

    def __init__(self, name: str, position: tuple[int, int]):
        self.name = name
        self.position = position

    @abstractmethod
    def do(self, program: Program):
        pass


class Start(Operator):
    """
    A system operator indicating that this is the beginning of the
    program.
    """

    def do(self, program):
        pass


class End(Operator):
    """
    End of program operator.
    Not included in languages (usually), it is used mainly as a system
    operator - added to the end of the program to finish it.
    """

    def do(self, program):
        program.runtime.is_running = False


# === original operators ===============================================


class Right(Operator):
    """
    Moves the tape pointer to the right.
    If the cell was the last one, it moves to the first one if the tape
    is looped, else it triggers an error.
    """

    def do(self, program):
        program.runtime.pointer += 1
        if program.runtime.pointer < program.config.TAPE_LEN:
            return

        if program.config.IS_LOOPED:
            program.runtime.pointer = 0
            return

        msg = "tape pointer out of range ({pointer} > {size})".format(
            pointer=program.runtime.pointer,
            size=program.config.TAPE_LEN - 1
        )
        raise ExecutionError(msg)


class Left(Operator):
    """
    Moves the pointer to the left.
    If there was the first (zero) cell, it moves the cursor to the last
    element if the tape is looped, else it generates an error.
    """

    def do(self, program):
        program.runtime.pointer -= 1
        if program.runtime.pointer >= 0:
            return

        if program.config.IS_LOOPED:
            program.runtime.pointer = program.config.TAPE_LEN - 1
            return

        msg = f"tape pointer out of range ({program.runtime.pointer} < 0)"
        raise ExecutionError(msg)


class Increment(Operator):
    """
    Increases the value of the current cell by 1.
    Since the original BrainFuck was implemented in languages with
    overflow, it either executes it (if necessary) or generates an error.
    """

    def do(self, program):
        new_val = program.runtime.current_val + 1
        overflowed_val = program.config.check_on_max_value(new_val)
        program.runtime.current_val = overflowed_val


class Decrement(Operator):
    """
    Reduces the value of the current cell by 1.
    Since the original BrainFuck was implemented in languages with
    overflow, it either executes it (if necessary) or generates an error.
    """

    def do(self, program):
        new_val = program.runtime.current_val - 1
        overflowed_val = program.config.check_on_min_value(new_val)
        program.runtime.current_val = overflowed_val


class Output(Operator):
    """
    Outputs the current cell as a Unicode character (without line break).
    If the cell value is out of Unicode, it generates an error.
    """

    UNICODE_MAX = 0x10ffff

    @classmethod
    def is_unicode(cls, char_code: int) -> bool:
        return 0 <= char_code < cls.UNICODE_MAX

    def do(self, program):
        char_code = program.runtime.current_val
        if not self.is_unicode(char_code):
            msg = "value is out of range of unicode ({value} <> [0:{max}])".format(
                value=char_code,
                max=self.UNICODE_MAX
            )
            raise ExecutionError(msg)
        print(chr(char_code), end="")
        program.runtime._linebreak_required = char_code != 10  # not "\n"


class Input(Operator):
    """
    Reads the character and puts its code in the cell.
    If more than one character is entered, only the first character is
    used.
    """

    def do(self, program):
        char = input("> ")  # TODO: ctrl-c
        char = char.lstrip(" ")[:1]
        char_code = ord(char or "\n")
        code = program.config.check_on_max_value(char_code)
        program.runtime.current_val = code


class While(Operator):
    """
    The beginning of the loop.
    If the value in the current cell is NOT zero, nothing happens.
    If the value is zero, it searches for the relevant close loop
    statement and moves the cursor to it. Nesting is taken into account;
    if the end of the program is found during the search, it is stopped.
    """

    def do(self, program):
        if program.runtime.current_val:
            return

        cursor = program.runtime.cursor
        nesting = 0
        while True:
            operator = program.runtime.operator
            if isinstance(operator, While):
                nesting += 1
            elif isinstance(operator, WhileEnd):
                nesting -= 1

            if nesting == 0:
                break
            elif isinstance(operator, End):
                program.runtime.cursor -= 1
                break
            cursor += 1

        program.runtime.cursor = cursor


class WhileEnd(Operator):
    """
    End of cycle.
    If the value in the current cell is null, nothing happens.
    If the value is not zero, the relevant loop opening statement (at
    the back) is searched for and the cursor is moved to it. Nesting is
    taken into account; if the beginning of the program is found during
    the search, an error is called.
    """

    def do(self, program):
        if not program.runtime.current_val:
            return

        cursor = program.runtime.cursor
        nesting = 0
        while True:
            operator = program.operators[cursor]
            if isinstance(operator, WhileEnd):
                nesting += 1
            elif isinstance(operator, While):
                nesting -= 1

            if nesting == 0:
                break
            elif isinstance(operator, Start):
                raise ExecutionError("unexpected end of loop")
            cursor -= 1

        program.runtime.cursor = cursor


# === extended operators ===============================================


class GiveSomeFishfood(Operator):
    """
    The joking operator from the Blub language.
    """

    def do(self, program):
        program._break_line()
        print("*Fishfood transfer takes place* - \"Blub!\"")
        program.runtime._linebreak_required = False


class Repeat(Operator):
    """
    Repeats the previous operator.
    May not work correctly with the `While` and `WhileEnd` operators.
    """

    def do(self, program):
        cursor = program.runtime.cursor - 1
        while cursor >= 0 and isinstance(program.operators[cursor], Repeat):
            cursor -= 1

        if isinstance(program.operators[cursor], Start):
            raise ExecutionError("no previous operator found")

        program.operators[cursor].do(program)


class GiveBanana(Operator):
    """
    The joking operator from the Ook language.
    """

    def do(self, program):
        program._break_line()
        print("*Banana transfer takes place* - \"Ook!\"")
        program.runtime._linebreak_required = False
