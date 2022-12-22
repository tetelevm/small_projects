import re
from abc import ABC, abstractmethod
from typing import Type, Optional

from operators import *
from program import Program


__all__ = [
    "Brainfuck",
    "Alphuck",
    "BinaryFuck",
    "BrainSymbol",
    "EmEmFuck",
    "German",
    "MessyScript",
    "MorseFuck",
    "Pewlang",
    "ReverseFuck",
    "Roadrunner",
    "Ternary",
    "Triplet",
    "UwU",
    "WholesomeFuck",
    "ZZZ",

    "Blub",
    "Fuckfuck",
    "Ook",
    "Pogaack",
]


# === bases ============================================================


class Interpreter(ABC):
    """
    Interpreter base class.
    Interpreters translate text code into an inner representation (a
    list of `Operator` objects), ready to be executed.
    The main method is `.translate()`, which returns a ready-to-execute
    program.
    """

    text: str
    operators: Optional[dict[str, Type[Operator]]]

    def __init__(self, text: str):
        self.text = text

    @abstractmethod
    def parse_text(self, text: str) -> list[Operator]:
        pass

    def translate(self) -> Program:
        """
        Parses the program text and does the system actions that parsing
        requires.
        Returns the program ready for execution.
        """

        operators = [
            Start("~start~", (0, 0)),
            *self.parse_text(self.text),
            End("~end~", (0, 0))
        ]
        return Program(self.text, operators)


class Trivial(Interpreter, ABC):
    """
    A class-label that shows that the language is a simple translation
    of the original BrainFuck without the addition of any operators or
    rules.
    """
    # Fun fact - BrainFuck is also a subclass :)


class Extended(Interpreter, ABC):
    """
    A class-label that shows that the language is backward compatible
    with BrainFuck*, but has some extension on top of it.

    * - by operator logic, not by specific writing
    """


class WithUniqueCommand(Interpreter, ABC):
    """
    A subclass of interpreters that have a unique mapping between a
    command and an operator. The main condition is that the commands
    cannot contain each other.
    That includes the original BF, more examples: UwU, GERMAN, Alphuck.
    """

    operators: dict[str, Type[Operator]]

    def parse_text(self, text) -> list[Operator]:
        operator_names = self.operators.keys()

        cursor = 0
        operators = []
        while cursor <= len(text):
            for name in operator_names:
                if not text[cursor:].startswith(name):
                    continue

                operator_class = self.operators[name]
                operator = operator_class(name, (cursor, cursor+len(name)))

                operators.append(operator)
                cursor += len(name)
                break
            else:
                cursor += 1

        return operators


class WithOrderedCommand(Interpreter, ABC):
    """
    In general, this is not particularly different from translations
    with unique commands, but the order of the commands is important
    here, since some commands may include others.
    Therefore, the parsing is a bit more complicated than in the
    original.
    Examples: EmEmFuck, zzz, Unibrain.
    """

    operators: dict[str, tuple[int, Type[Operator]]]

    def parse_text(self, text) -> list[Operator]:
        sorted_operators = sorted(self.operators.items(), key=lambda item: item[1][0])
        operator_names = [item[0] for item in sorted_operators]

        cursor = 0
        operators = []
        while cursor <= len(self.text):
            for name in operator_names:
                if not self.text[cursor:].startswith(name):
                    continue

                operator_class = self.operators[name][1]
                operator = operator_class(name, (cursor, cursor+len(name)))

                operators.append(operator)
                cursor += len(name)
                break
            else:
                cursor += 1

        return operators


class CustomCommand(Interpreter, ABC):
    """
    A base class for interpreters that have a custom text-to-operator
    translation.
    Examples: Oof, Binaryfuck, Unibrain.
    """
    operators = {}


# === trivial languages ================================================


class Brainfuck(Trivial, WithUniqueCommand):
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


class Alphuck(Trivial, WithUniqueCommand):
    """
    A simple translation of BrainFuck, a matching:
    +---+---+
    | > | a |
    | < | c |
    | + | e |
    | - | i |
    | . | j |
    | , | o |
    | [ | p |
    | ] | s |
    +---+---+
    """

    operators = {
        "a": Right,
        "c": Left,
        "e": Increment,
        "i": Decrement,
        "j": Output,
        "o": Input,
        "p": While,
        "s": WhileEnd,
    }


class BinaryFuck(Trivial, WithUniqueCommand):
    """
    This language is a trivial translation of BrainFuck, but with the `1`
    symbol at the beginning of the text.
    Matching:
    +---+-----+
    | > | 010 |
    | < | 011 |
    | + | 000 |
    | - | 001 |
    | . | 100 |
    | , | 101 |
    | [ | 110 |
    | ] | 111 |
    +---+-----+
    """

    operators = {
        "010": Right,
        "011": Left,
        "000": Increment,
        "001": Decrement,
        "100": Output,
        "101": Input,
        "110": While,
        "111": WhileEnd,
    }

    def parse_text(self, text) -> list[Operator]:
        text = text[1:]  # remove the first `1`
        operators = super().parse_text(text)
        for operator in operators:
            # consider the first `1`
            operator.position = (operator.position[0] + 1, operator.position[1] + 1)
        return operators


class BrainSymbol(Trivial, WithUniqueCommand):
    """
    A simple translation of BrainFuck, a matching:
    +---+---+
    | > | ! |
    | < | @ |
    | + | # |
    | - | $ |
    | . | % |
    | , | ^ |
    | [ | & |
    | ] | * |
    +---+---+
    """

    operators = {
        "!": Right,
        "@": Left,
        "#": Increment,
        "$": Decrement,
        "%": Output,
        "^": Input,
        "&": While,
        "*": WhileEnd,
    }


class EmEmFuck(Trivial, WithUniqueCommand):
    # original name: !!Fuck
    """
    A simple translation of BrainFuck, a matching:
    +---+---------------+
    | > | !!!!!#        |
    | < | !!!!!!#       |
    | + | !!!!!!!#      |
    | - | !!!!!!!!#     |
    | . | !!!!!!!!!!#   |
    | , | !!!!!!!!!#    |
    | [ | !!!!!!!!!!!#  |
    | ] | !!!!!!!!!!!!# |
    +---+---------------+
    """

    operators = {
        "!!!!!#": Right,
        "!!!!!!#": Left,
        "!!!!!!!#": Increment,
        "!!!!!!!!#": Decrement,
        "!!!!!!!!!!#": Output,
        "!!!!!!!!!#": Input,
        "!!!!!!!!!!!#": While,
        "!!!!!!!!!!!!#": WhileEnd,
    }


class German(Trivial, WithUniqueCommand):
    """
    A simple translation of BrainFuck, a matching:
    +---+-----------------+
    | > | LINKS           |
    | < | RECHTS          |
    | + | ADDITION        |
    | - | SUBTRAKTION     |
    | . | EINGABE         |
    | , | AUSGABE         |
    | [ | SCHLEIFENANFANG |
    | ] | SCHLEIFENENDE   |
    +---+-----------------+
    """

    operators = {
        "LINKS": Right,
        "RECHTS": Left,
        "ADDITION": Increment,
        "SUBTRAKTION": Decrement,
        "EINGABE": Output,
        "AUSGABE": Input,
        "SCHLEIFENANFANG": While,
        "SCHLEIFENENDE": WhileEnd,
    }


class MessyScript(Trivial, WithUniqueCommand):
    """
    A simple translation of BrainFuck, a matching:
    +---+------------------------------------------------------------------------------------------------+
    | > | 930pl[wer;lr[p[lwetl[erwltrewt[er;t3l.t;43.';w]er\e]e;g[er.][.rt[.e[w]r[                       |
    | < | \];[]lr[plp[r[pelpr[,gp[lsp[glr[pt,g[pr,g[lsg[plfsdgdsfpl[erlt[lwt[43[]5l4[;.tr.               |
    | + | 20ri-4;t[5;t'[y;e'teu;354y;;56;'5lu;y65l'ytyl';ry;rtly;t'yl'r;y'                               |
    | - | ];ae][flw[er.[w;r';ew.'rt;e';,erf/r;t.e'.fre.f'r;.rg;el[rw][p43p3                              |
    | . | ][][e[w]prepf][eg]rpe[t]lre[]lgr]o320wr89`]2l1]p`l23pr2o4]2lf]2;r][32;r][2``]234;][23          |
    | , | ]\]p][l[weo[p4o40ti40er0iteotp[r]23;[rle[wptlo34wtp[rel[1;`][l3[l[rplew[fl[`1[l[wlr[pewlr[p    |
    | [ | \];[]fl[roeotp[ore][gper][g;rw][;g][r;eg][le]f[el]f]w[r][wper][pwtlregl]erl][;]e;][e;t[erpt][p |
    | ] | \[]pe[3202-432o-0rkepk[1[pwplwpflerp[glep[r[er[pe[tpre][]t\][p[0-=30-323-=232[r[ept[erg[erpt]  |
    +---+------------------------------------------------------------------------------------------------+
    """

    operators = {
        "930pl[wer;lr[p[lwetl[erwltrewt[er;t3l.t;43.';w]er\e]e;g[er.][.rt[.e[w]r[": Right,
        "\];[]lr[plp[r[pelpr[,gp[lsp[glr[pt,g[pr,g[lsg[plfsdgdsfpl[erlt[lwt[43[]5l4[;.tr.": Left,
        "20ri-4;t[5;t'[y;e'teu;354y;;56;'5lu;y65l'ytyl';ry;rtly;t'yl'r;y'": Increment,
        "];ae][flw[er.[w;r';ew.'rt;e';,erf/r;t.e'.fre.f'r;.rg;el[rw][p43p3": Decrement,
        "][][e[w]prepf][eg]rpe[t]lre[]lgr]o320wr89`]2l1]p`l23pr2o4]2lf]2;r][32;r][2``]234;][23": Output,
        "]\]p][l[weo[p4o40ti40er0iteotp[r]23;[rle[wptlo34wtp[rel[1;`][l3[l[rplew[fl[`1[l[wlr[pewlr[p": Input,
        "\];[]fl[roeotp[ore][gper][g;rw][;g][r;eg][le]f[el]f]w[r][wper][pwtlregl]erl][;]e;][e;t[erpt][p": While,
        "\[]pe[3202-432o-0rkepk[1[pwplwpflerp[glep[r[er[pe[tpre][]t\][p[0-=30-323-=232[r[ept[erg[erpt]": WhileEnd,
    }


class MorseFuck(Trivial, WithUniqueCommand):
    """
    A simple translation of BrainFuck, a matching:
    +---+-----+
    | > | .-- |
    | < | --. |
    | + | ..- |
    | - | -.. |
    | . | -.- |
    | , | .-. |
    | [ | --- |
    | ] | ... |
    +---+-----+
    """

    operators = {
        ".--": Right,
        "--.": Left,
        "..-": Increment,
        "-..": Decrement,
        "-.-": Output,
        ".-.": Input,
        "---": While,
        "...": WhileEnd,
    }


class Pewlang(Trivial, WithUniqueCommand):
    """
    A simple translation of BrainFuck, a matching:
    +---+-----+
    | > | pew |
    | < | Pew |
    | + | pEw |
    | - | peW |
    | . | pEW |
    | , | PEw |
    | [ | PeW |
    | ] | PEW |
    +---+-----+
    """

    operators = {
        "pew": Right,
        "Pew": Left,
        "pEw": Increment,
        "peW": Decrement,
        "pEW": Output,
        "PEw": Input,
        "PeW": While,
        "PEW": WhileEnd,
    }


class ReverseFuck(Trivial, WithUniqueCommand):
    """
    A simple translation of BrainFuck, a matching:
    +---+---+
    | + | - |
    | - | + |
    | < | > |
    | > | < |
    | . | , |
    | , | . |
    | [ | ] |
    | ] | [ |
    +---+---+
    """

    operators = {
        "-": Right,
        "+": Left,
        ">": Increment,
        "<": Decrement,
        ",": Output,
        ".": Input,
        "]": While,
        "[": WhileEnd,
    }


class Roadrunner(Trivial, WithUniqueCommand):
    """
    A simple translation of BrainFuck, a matching:
    +---+------+
    | > | meeP |
    | < | Meep |
    | + | mEEp |
    | - | MeeP |
    | . | MEEP |
    | , | meep |
    | [ | mEEP |
    | ] | MEEp |
    +---+------+
    """

    operators = {
        "meeP": Right,
        "Meep": Left,
        "mEEp": Increment,
        "MeeP": Decrement,
        "MEEP": Output,
        "meep": Input,
        "mEEP": While,
        "MEEp": WhileEnd,
    }


class Ternary(Trivial, WithUniqueCommand):
    """
    A simple translation of BrainFuck, a matching:
    +---+----+
    | > | 01 |
    | < | 00 |
    | + | 11 |
    | - | 10 |
    | . | 20 |
    | , | 21 |
    | [ | 02 |
    | ] | 12 |
    +---+----+
    """

    operators = {
        "01": Right,
        "00": Left,
        "11": Increment,
        "10": Decrement,
        "20": Output,
        "21": Input,
        "02": While,
        "12": WhileEnd,
    }


class Triplet(Trivial, WithUniqueCommand):
    """
    A simple translation of BrainFuck, a matching:
    +---+-----+
    | > | 001 |
    | < | 100 |
    | + | 111 |
    | - | 000 |
    | . | 010 |
    | , | 101 |
    | [ | 110 |
    | ] | 011 |
    +---+-----+
    """

    operators = {
        "001": Right,
        "100": Left,
        "111": Increment,
        "000": Decrement,
        "010": Output,
        "101": Input,
        "110": While,
        "011": WhileEnd,
    }


class UwU(Trivial, WithUniqueCommand):
    """
    A simple translation of BrainFuck, a matching:
    +---+-----+
    | > | OwO |
    | < | °w° |
    | + | UwU |
    | - | QwQ |
    | . | @w@ |
    | , | >w< |
    | [ | ~w~ |
    | ] | ¯w¯ |
    +---+-----+
    """

    operators = {
        "OwO": Right,
        "°w°": Left,
        "UwU": Increment,
        "QwQ": Decrement,
        "@w@": Output,
        ">w<": Input,
        "~w~": While,
        "¯w¯": WhileEnd,
    }


class WholesomeFuck(Trivial, WithOrderedCommand):
    """
    A simple translation of BrainFuck, a matching:
    +---+-----+
    | > | :>  |
    | < | :<  |
    | + | :>> |
    | - | :<< |
    | . | ;<< |
    | , | ;>> |
    | [ | ;<  |
    | ] | ;>  |
    +---+-----+
    """

    operators = {
        ":>": (4, Right),
        ":<": (5, Left),
        ":>>": (0, Increment),
        ":<<": (1, Decrement),
        ";<<": (2, Output),
        ";>>": (3, Input),
        ";<": (6, While),
        ";>": (7, WhileEnd),
    }


class ZZZ(Trivial, WithOrderedCommand):
    """
    A simple translation of BrainFuck, a matching:
    +---+------+
    | > | zz   |
    | < | -zz  |
    | + | z    |
    | - | -z   |
    | . | zzz  |
    | , | -zzz |
    | [ | z+z  |
    | ] | z-z  |
    +---+------+
    """

    operators = {
        "zz": (2, Right),
        "-zz": (3, Left),
        "z": (7, Increment),
        "-z": (6, Decrement),
        "zzz": (0, Output),
        "-zzz": (1, Input),
        "z+z": (4, While),
        "z-z": (5, WhileEnd),
    }


# === extended languages ===============================================


class Blub(Extended, WithUniqueCommand):
    """
    A translation of BrainFuck with a small addition.
    Matching:
    +---+-------------+
    | > | Blub. Blub? |
    | < | Blub? Blub. |
    | + | Blub. Blub. |
    | - | Blub! Blub! |
    | . | Blub! Blub. |
    | , | Blub. Blub! |
    | [ | Blub! Blub? |
    | ] | Blub? Blub! |
    +---+-------------+
    Extension:
    +-------------+---------------------------------------------------------+
    | Blub? Blub? | (joking operator) Give the memory pointer some fishfood |
    +-------------+---------------------------------------------------------+
    """

    operators = {
        "Blub. Blub?": Right,
        "Blub? Blub.": Left,
        "Blub. Blub.": Increment,
        "Blub! Blub!": Decrement,
        "Blub! Blub.": Output,
        "Blub. Blub!": Input,
        "Blub! Blub?": While,
        "Blub? Blub!": WhileEnd,
        "Blub? Blub?": GiveSomeFishfood,
    }


class Fuckfuck(Extended, CustomCommand):
    """
    A language with a custom realization. It is an extension of the
    original BrainFuck.
    Matching:
    +---+------+
    | > | f**k |
    | < | s**g |
    | + | b**b |
    | - | t**s |
    | . | c**k |
    | , | k**b |
    | [ | a**e |
    | ] | b**t |
    +---+------+
    But any letter can take the place of the `*` characters.
    In this implementation it can only be Latin letters, numbers or
    underscore.

    Extension:
    +---+-------------------------------+
    | ! | Repeats the previous operator |
    +---+-------------------------------+
    """

    operator_symbs = {
        "fk": Right,
        "sg": Left,
        "bb": Increment,
        "ts": Decrement,
        "ck": Output,
        "kb": Input,
        "ae": While,
        "bt": WhileEnd,
    }

    def parse_text(self, text) -> list[Operator]:
        pattern = "(!)|" + "|".join(
            fr"({f}\w\w{s})"
            for (f, s) in self.operator_symbs.keys()
        )

        operators = []
        for res in re.finditer(pattern, self.text):
            name = res.group()
            operator_class = (
                self.operator_symbs[name[0] + name[-1]]
                if name != "!" else
                Repeat
            )

            operators.append(operator_class(name, res.span()))

        return operators


class Ook(Extended, WithUniqueCommand):
    """
    A translation of BrainFuck with a small addition.
    Matching:
    +---+-----------+
    | > | Ook. Ook? |
    | < | Ook? Ook. |
    | + | Ook. Ook. |
    | - | Ook! Ook! |
    | . | Ook! Ook. |
    | , | Ook. Ook! |
    | [ | Ook! Ook? |
    | ] | Ook? Ook! |
    +---+-----------+
    Extension:
    +-----------+----------------------------------------------------+
    | Ook? Ook? | (joking operator) Give the memory pointer a banana |
    +-----------+----------------------------------------------------+
    """

    operators = {
        "Ook. Ook?": Right,
        "Ook? Ook.": Left,
        "Ook. Ook.": Increment,
        "Ook! Ook!": Decrement,
        "Ook! Ook.": Output,
        "Ook. Ook!": Input,
        "Ook! Ook?": While,
        "Ook? Ook!": WhileEnd,
        "Ook? Ook?": GiveBanana,
    }


class Pogaack(Extended, WithUniqueCommand):
    """
    A language with a custom realization. It is an extension of the
    original BrainFuck.
    Matching:
    +---+-----------+
    | > | pogack!   |
    | < | pogaack!  |
    | + | pogaaack! |
    | - | poock!    |
    | . | pogaaack? |
    | , | poock?    |
    | [ | pogack?   |
    | ] | pogaack?  |
    +---+-----------+
    But any letter can take the place of the `*` characters.
    In this implementation it can only be Latin letters, numbers or
    underscore.

    Extension:
    +-------+-------------------------------+
    | pock! | Repeats the previous operator |
    +-------+-------------------------------+
    """

    operators = {
        "pogack!": Right,
        "pogaack!": Left,
        "pogaaack!": Increment,
        "poock!": Decrement,
        "pogaaack?": Output,
        "poock?": Input,
        "pogack?": While,
        "pogaack?": WhileEnd,
        "pock!": Repeat,
    }
