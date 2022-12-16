from abc import ABC, abstractmethod
from typing import Type, Optional

from operators import *


__all__ = [
    "Interpreter",

    "Brainfuck",
]


class Interpreter(ABC):
    """
    Interpreter base class.
    Interpreters translate text code into an inner representation (a
    list of `Operator` objects), ready to be executed.
    """

    text: str
    operators: Optional[dict[str, Type[Operator]]]

    def __init__(self, text: str):
        self.text = text

    @abstractmethod
    def translate(self) -> list[Operator]:
        pass

    def make_error_info(self, start: int, end: int) -> tuple[str, str]:
        """
        Returns the context of the operator and its selection in the
        context.
        The context is the operator itself and some characters to the
        right and left. Operators that are too large are minimized,
        indentation is cut to the end of the lines. Underscores are done
        in the same way as in Python.

        Example:
        |   some text        OperatorWi...ryLongName           some text|
        |                    ^^^^^^^^^^^^^^^^^^^^^^^                    |
        """

        operator_text = self.text[start:end]
        if len(operator_text) > 30:
            operator_text = operator_text[:10] + "..." + operator_text[-10:]

        indent = 20

        previous = self.text[max(start - indent, 0):start]
        if (ind := previous.rfind("\n")) >= 0:
            previous = previous[ind+1:]

        subsequent = self.text[end:end+indent]
        if (ind := subsequent.find("\n")) >= 0:
            subsequent = subsequent[:ind]

        context = previous + operator_text + subsequent
        underline = " "*len(previous) + "^"*len(operator_text) + " "*len(subsequent)
        return context, underline


class WithUniqueCommand(Interpreter, ABC):
    """
    A subclass of interpreters that have a unique mapping between a
    command and an operator. The main condition is that the commands
    cannot contain each other.
    That includes the original BF, more examples: UwU, GERMAN, Alphuck.
    """

    operators: dict[str, Type[Operator]]

    def translate(self) -> list[Operator]:
        operator_names = self.operators.keys()
        operators = []

        cursor = 0
        while cursor <= len(self.text):
            for name in operator_names:
                if not self.text[cursor:].startswith(name):
                    continue

                operator_class = self.operators[name]
                error_info = self.make_error_info(cursor, cursor+len(name))
                operator = operator_class(name, error_info)

                operators.append(operator)
                cursor += len(name)
                break
            else:
                cursor += 1

        operators.append(End("~end~", ("", "")))
        return operators


class Brainfuck(WithUniqueCommand):
    """
    The standard realization of the BrainFuck language, the other
    similar languages are either extensions or translations.

    The point is simple:
    - there is a tape (array) of bytes, initially all filled with zeros
    - there is a pointer which refers to a cell of the tape, initially
        referring to the first ("zero") cell
    - there are 8 commands which are used to interact with the tape,
        pointer and input-output:
    +---+-------------------------------------------------------------------+
    | > | move the pointer to the right                                     |
    | < | move the pointer to the left                                      |
    | + | increment the memory cell at the pointer                          |
    | - | decrement the memory cell at the pointer                          |
    | . | output the character signified by the cell at the pointer         |
    | , | input a character and store it in the cell at the pointer         |
    | [ | jump past the matching ] if the cell at the pointer is 0          |
    | ] | jump back to the matching [ if the cell at the pointer is nonzero |
    +---+-------------------------------------------------------------------+
    All other characters are ignored.
    Input/output is converted to number/symbol by Unicode.
    """

    operators = {
        ">": Right,
        "<": Left,
        "+": Increment,
        "-": Decrement,
        ".": Output,
        ",": Input,
        "[": While,
        "]": WhileEnd,
    }
