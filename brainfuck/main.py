"""
This program is an interpreter of the esoteric language Brainfuck.
Description of the original language:

There is a tape of 30_000 elements and a pointer to a cell in the tape.
There are also 8 characters available:
> - go to the next cell
< - go to the previous cell
+ - increment the value in the current cell by 1
- - decrement the value in the current cell by 1
. - print the value from the current cell
, - input the value and save it in the current cell
[ - if the value of the current cell is ZERO, go to the character after ] (*)
] - if the value of the current cell is NOT ZERO, go backward to symbol [ (*)

(*) taking into account nesting
"""

from pathlib import Path

from runtime import RunTime
from interpreters import Brainfuck


__all__ = [
    "run_program",
]


def run_program(text: str, language: str = "Brainfuck"):
    """
    Runs the program text with a specific program language.
    """

    interpreter = globals()[language]
    translated_program = interpreter(text).translate()
    RunTime(translated_program).execute()


def main():
    language = "Brainfuck"
    text_path = Path(__file__).parent / "helloworlds" / language.lower()
    with open(text_path) as file:
        text = file.read()
    run_program(text, language)


if __name__ == "__main__":
    main()
