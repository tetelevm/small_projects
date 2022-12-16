from config import Config
from operators import Operator


class RunTime:
    """
    The class of the program's runtime that executes a list of operators.
    It has a tape and a pointer to its cell. It also has a cursor to the
    command that is currently being executed. The program stops when the
    `is_running` parameter changes.
    """

    tape: list[int]
    pointer: int
    cursor: int
    is_running: bool

    _linebreak_required: bool

    def __init__(self, operators: list[Operator]):
        self.operators = operators
        self.cursor = 0
        self.pointer = 0
        self.tape: list[int] = [0] * Config.TAPE_LEN
        self.is_running = True

        self._linebreak_required = False

    def execute(self):
        """
        The list of commands is executed until the program stops.
        If there is an error, it looks for the command that triggered it
        and displays information about the error.
        """

        self.cursor = 0
        while self.is_running:
            operator = self.operators[self.cursor]
            try:
                operator.do(self)
            except ValueError as error:
                msg = self.get_error_msg(operator, error)
                print(msg)
                self.is_running = False
            self.cursor += 1

    def get_error_msg(self, operator: Operator, error: Exception) -> str:
        """
        Outputs a formatted string about an error that occurred while
        executing the operator.
        """

        msg = (
            ("\n" if self._linebreak_required else "")
            + "RunTime error ["
            + f"operator: ` {operator.name} `;"
            + f" pointer: {self.pointer}"
            + f"]:\n{operator.error_info[0]}\n{operator.error_info[1]}\n"
            + str(error.args[0])
        )
        return msg
