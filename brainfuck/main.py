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

import sys
from pathlib import Path

from runtime import RunTime
from interpreters import __all__ as all_languages
from interpreters import *


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
    """
    Runs by default and executes the HelloWorld-script from the
    `helloworlds` directory.
    It has one parameter - startup language. Available languages can be
    found in `interpreters.__all__`.

    > python3 main.py Brainfuck
    """

    try:
        language = sys.argv[1]
    except IndexError:
        language = "Brainfuck"
    if language not in all_languages:
        raise ValueError(f"unknown language <{language}>")

    text_path = Path(__file__).parent / "helloworlds" / language.lower()
    with open(text_path) as file:
        text = file.read()
    run_program(text, language)


if __name__ == "__main__":
    main()
