from __future__ import annotations
from typing import Protocol

from exeptions import ExecutionError
from config import Config


__all__ = [
    "Program",
]


class Operator(Protocol):
    """
    Operator interface. This is the minimum set of parameters.
    """

    name: str
    position: tuple[int, int]

    def do(self, program: Program):
        pass


class RunTime:
    """
    Program runtime, that is, the set of things and entities that change
    in the program at execution time.
    """

    tape: list[int]
    pointer: int
    cursor: int
    is_running: bool
    params: dict

    _linebreak_required: bool

    def __init__(self, program: Program):
        self.program = program

        self.cursor = 0
        self.pointer = 0
        self.tape: list[int] = [0] * Config.TAPE_LEN
        self.is_running = True
        self.params = dict()

        self._linebreak_required = False

    def execute(self):
        """
        The list of commands is executed until the program stops.
        If there is an error, it looks for the command that triggered it
        and displays information about the error.
        """

        self.cursor = 0
        while self.is_running:
            self.operator.do(self.program)
            self.cursor += 1

    @property
    def operator(self) -> Operator:
        return self.program.operators[self.cursor]

    @property
    def current_val(self) -> int:
        return self.tape[self.pointer]

    @current_val.setter
    def current_val(self, value: int):
        self.tape[self.pointer] = value


class Program:
    """
    The class of the program that executes a list of operators.
    It has the program itself (list of operators), the runtime, the
    source data and the startup configuration.
    It executes the program and displays errors.
    Nothing changes here, all the changes are in the RunTime.
    """

    text: str
    operators: list[Operator]
    config: Config
    runtime: RunTime

    def __init__(self, text: str, operators: list[Operator], config: Config = None):
        self.text = text
        self.operators = operators
        self.config = config or Config()
        self.runtime = RunTime(self)

    def run(self):
        try:
            self.runtime.execute()
        except ExecutionError as error:
            # error in program logic
            self._break_line()
            msg = self.get_error_msg(error)
            print(msg)
        except Exception as error:
            # some kind of internal error
            self._break_line()
            print("There was some kind of internal error:")
            print(error.args[0])

    def _break_line(self):
        """
        Breaks the line if necessary. Used to display errors, for example.
        """
        if self.runtime._linebreak_required:
            print()

    def get_error_msg(self, error: ExecutionError) -> str:
        """
        Returned a formatted string about an error that occurred while
        executing the operator.
        """

        operator = self.runtime.operator
        context, underline = self.make_error_info(*operator.position)
        msg = (
            "RunTime error ["
            + f"operator: ` {operator.name} `;"
            + f" pointer: {self.runtime.pointer}"
            + f"]:\n{context}\n{underline}\n"
            + str(error.args[0])
        )
        return msg

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
