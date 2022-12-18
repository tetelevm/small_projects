from abc import ABC, abstractmethod
from typing import Type, Optional

from operators import *


__all__ = [
    "Brainfuck",
    "Alphuck",
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
    "Ook",
]


# === bases ============================================================


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

    def translate(self) -> list[Operator]:
        operator_names = self.operators.keys()

        cursor = 0
        operators = []
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


class WithOrderedCommand(Interpreter, ABC):
    """
    In general, this is not particularly different from translations
    with unique commands, but the order of the commands is important
    here, since some commands may include others.
    Therefore, the parsing is a bit more complicated than in the
    original.
    That includes the original BF, more examples: EmEmFuck, zzz, Unibrain.
    """

    operators: dict[str, tuple[int, Type[Operator]]]

    def translate(self) -> list[Operator]:
        sorted_operators = sorted(self.operators.items(), key=lambda item: item[1][0])
        operator_names = [item[0] for item in sorted_operators]

        cursor = 0
        operators = []
        while cursor <= len(self.text):
            for name in operator_names:
                if not self.text[cursor:].startswith(name):
                    continue

                operator_class = self.operators[name][1]
                error_info = self.make_error_info(cursor, cursor+len(name))
                operator = operator_class(name, error_info)

                operators.append(operator)
                cursor += len(name)
                break
            else:
                cursor += 1

        operators.append(End("~end~", ("", "")))
        return operators


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
















