## BrainFuck

BrainFuck language interpreter, which can be easily modified for translations
and extensions of the original language.

### Description of the language

[Interesting link](https://esolangs.org/) <- the description of the implemented
languages was taken from here.

Brainfuck operates on an array of memory cells, each initially set to zero.
(In the original implementation, the array was 30,000 cells long, but this may
not be part of the language specification; different sizes for the array length
and cell size give different variants of the language).

There is a pointer, initially pointing to the first memory cell.

The commands are:
- `>` - Move the pointer to the right
- `<` - Move the pointer to the left
- `+` - Increment the memory cell at the pointer
- `-` - Decrement the memory cell at the pointer
- `.` - Output the character signified by the cell at the pointer
- `,` - Input a character and store it in the cell at the pointer
- `[` - Jump past the matching `]` if the cell at the pointer is 0
- `]` - Jump back to the matching `[` if the cell at the pointer is nonzero

All characters other than `><+-.,[]` should be considered comments and ignored.

Since the language is strange and simple, there have appeared many translations
of it (modified way of describing the operators), extensions (other operators
have been added) or complications (a strong revision of the language inspired by
the original BrainFuck. Some (and maybe most) are also implemented here.

### Structure of the project

There are several major entities:

- operator: a specific operator that performs a single function, such as one that
    translates a pointer or that opens a loop. A set of operators is a compiled
    program text.
- configuration: the set of parameters of the cells and tape with which the
    program is executed, For example, the maximum cell size or tape loops.
- runtime: it keeps the state of the executable program - tape, pointer, system
    variables.
- program: an entity that contains all the information about a program - the set
    of operators, run configuration, runtime.
- interpreter: translates the text into a program ready to execute.

With this structure, it is very easy to make translations and additions to the
language: you just need to write an interpreter for translation (for simple
translations with unique commands just describe the mapping to the original), or
for extensions just create a new operator and add it to your interpreter.

For example, here is a valid interpreter for `><+-.,[]` => `qwertyui` translation:

```python
class NewLanguage(Trivial, WithUniqueCommand):
    operators = {
        "q": Right,
        "w": Left,
        "e": Increment,
        "r": Decrement,
        "t": Output,
        "y": Input,
        "u": While,
        "i": WhileEnd,
    }
```

The translation call returns the program ready to be executed:

```python
text_of_program = "eeeeuqeeeewriquqeeeewriqt"  # displays `@`
progam = NewLanguage(text_of_program).translate()
program.run()
```

### Running

The project uses Python3.11 and there are no additional dependencies.

The simplest running is:

```shell
python3 main.py
```

This command will execute a `hello-world`-script for the BrainFuck language. To
specify a concrete language (implemented in the project) you need to call:

```shell
python3 main.py {NameOfLanguage}
```

List of implemented languages:

Brainfuck, AAA, Alphuck, BinaryFuck, BrainSymbol, EmEmFuck, German, Headsecks,
MessyScript, MorseFuck, Oof, Pewlang, ReverseFuck, Roadrunner, Ternary, Triplet,
Unibrain, UwU, WholesomeFuck, Wordfuck, ZZZ, Blub, Fuckfuck, Ook, Pogaack,
Braincrash, PocketBF, InstructionPointerBF

A description for them is available in the code or [here](https://esolangs.org/wiki/Category:Brainfuck_equivalents).

If you want to run an own program, it is a bit more complicated, because you
need to read the program text yourself and then do it in the python console:

```python
from interpreters import _YourLanguage_

progam = _YourLanguage_(text_of_program).translate()
program.run()
```
