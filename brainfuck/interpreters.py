import re
from abc import ABC, abstractmethod
from typing import Type, Optional

from operators import *
from program import Program


__all__ = [
    "Brainfuck",

    "AAA",
    "Alphuck",
    "BinaryFuck",
    "BrainSymbol",
    "EmEmFuck",
    "German",
    "Headsecks",
    "MessyScript",
    "MorseFuck",
    "Oof",
    "Pewlang",
    "ReverseFuck",
    "Roadrunner",
    "Ternary",
    "Triplet",
    "Unibrain",
    "UwU",
    "WholesomeFuck",
    "Wordfuck",
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


class AAA(Trivial, WithUniqueCommand):
    """
    A simple translation of BrainFuck, with the additional condition that
    everything inside the brackets is a comment:
    `AAAA ( AAaa AAAA) aaaa`
     ++++   ---- ----  ++++

    Matching:
    +---+------+
    | > | aAaA |
    | < | AAaa |
    | + | AAAA |
    | - | AaAa |
    | . | aAaa |
    | , | aaaa |
    | [ | aaAA |
    | ] | aaaA |
    +---+------+

    Small extension:
    +--------+-----------------------------------+
    | (smth) |  All inside brackets are comments |
    +--------+-----------------------------------+
    This version supports parentheses nesting:
    `AAAA (AAAA (AAAA))`
     ++++  ----  ----
    """

    operators = {
        "aAaA": Right,
        "AAaa": Left,
        "AAAA": Increment,
        "AaAa": Decrement,
        "aAaa": Output,
        "aaaa": Input,
        "aaAA": While,
        "aaaA": WhileEnd,
    }

    RANGE = tuple[int, int]

    def get_comment_ranges(self, text: str) -> list[RANGE]:
        """
        Searches all open-close bracket (comment) ranges in the text.
        If a parenthesis is opened multiple times, it is expected to be
        closed multiple times (nesting is supported).
        If a parenthesis is not closed until the end of the text, the
        comment continues until the end.

        `smth smth ( smth ( smth ) smth ) smth smth )  smth ( smthsmth`
                   ######################                   ##########
        """

        nesting = 0
        start = -1
        ranges = []
        for (num, char) in enumerate(text):
            if char == "(":
                nesting += 1
                if nesting == 1:
                    # start of comment
                    start = num

            if char == ")":
                nesting -= 1
                if nesting < 0:
                    # single bracket, not a comment
                    nesting = 0
                    continue
                elif nesting == 0:
                    # end of comment
                    ranges.append((start, num))
                    start = -1

        if start != -1:
            # comment continues until the end of the text
            ranges.append((start, len(text)))

        return ranges

    def is_not_comment(self, operator: Operator, ranges: list[RANGE]) -> bool:
        """
        Checks whether the operator is written inside or outside the
        comments. Ranges are expected to be non-overlapping and sorted
        in ascending order.
        """

        # it can be modified into a binary search
        for range_ in ranges:
            if range_[1] < operator.position[0]:
                continue
            if range_[0] > operator.position[1]:
                break
            return False

        return True

    def parse_text(self, text):
        all_operators = super().parse_text(text)
        comment_ranges = self.get_comment_ranges(text)

        operators = []
        for operator in all_operators:
            if self.is_not_comment(operator, comment_ranges):
                operators.append(operator)

        return operators


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


class Headsecks(Trivial, CustomCommand):
    """
    A trivial BrainFuck translation. The specific character is that all
    symbols, or rather their code, are used as operators. The operator
    is chosen depending on the remainder of the division of the code by
    `8` (the number of operators).
    Matching:
    +---+---+
    | > | 3 |
    | < | 2 |
    | + | 0 |
    | - | 1 |
    | . | 4 |
    | , | 5 |
    | [ | 6 |
    | ] | 7 |
    +---+---+
    """

    operator_remainder = {
        3: Right,
        2: Left,
        0: Increment,
        1: Decrement,
        4: Output,
        5: Input,
        6: While,
        7: WhileEnd,
    }

    def parse_text(self, text):
        operators = []
        for cursor in range(len(text)):
            char = text[cursor]
            operator_class = self.operator_remainder[ord(char) % 8]
            operator = operator_class(char, (cursor, cursor+1))
            operators.append(operator)
        return operators


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


class Oof(Trivial, CustomCommand):
    """
    A trivial BrainFuck translation.
    The specifics are in the description of the operators:
    the operator is a word of the form `oo...of` (several `o` and at the
    end `f`), the type of operator is taken by the formula
    `count("o") % 8 + 1`
    and the number of repeats
    `count("o") // 8`.
    Matching:
    +---+---+
    | > | 1 |
    | < | 2 |
    | + | 3 |
    | - | 4 |
    | . | 5 |
    | , | 6 |
    | [ | 7 |
    | ] | 8 |
    +---+---+
    """

    operator_remainder: dict[int, tuple[type[Operator], str]] = {
        1: (Right, "f"),
        2: (Left, "of"),
        3: (Increment, "oof"),
        4: (Decrement, "ooof"),
        5: (Output, "oooof"),
        6: (Input, "ooooof"),
        7: (While, "oooooof"),
        8: (WhileEnd, "ooooooof"),
    }

    def parse_text(self, text):
        pattern = r"[o]{1,}f"

        operators = []
        for mat in re.finditer(pattern, text):
            operator_group = mat.group()
            operator_kind = (len(operator_group) - 1) % 8 + 1
            operator_type, name = self.operator_remainder[operator_kind]
            count = (len(operator_group) - 1) // 8

            for operator_num in range(count):
                start = mat.start() + operator_num * 8
                operator = operator_type(name, (start, start+8))
                operators.append(operator)

        return operators


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


class Unibrain(Trivial, CustomCommand):
    """
    A trivial BrainFuck translation.
    The specificity is that the operator is a single word. The word is
    not any concrete word, it can be any word, but it must consist of
    repeating parts (`QweQwe`, `XXX`, `O_oO_oO_oO_o`). The number of
    repetitions is how it affects the choice of operator.
    If a word can be divided by more than one way (`++++` < 1, 2, 4),
    the highest number is used.
    Matching:
    +---+---+
    | > | 1 |
    | < | 2 |
    | + | 3 |
    | - | 4 |
    | . | 5 |
    | , | 6 |
    | [ | 7 |
    | ] | 8 |
    +---+---+
    """

    operator_remainder = {
        1: Right,
        2: Left,
        3: Increment,
        4: Decrement,
        5: Output,
        6: Input,
        7: While,
        8: WhileEnd,
    }

    def get_portion(self, word: str, portion: int) -> str:
        return word[:len(word) // portion]

    def find_repetitions_count(self, word: str) -> int:
        for portion in range(8, 0, -1):
            if (
                    len(word) % portion == 0
                    and self.get_portion(word, portion) * portion == word
            ):
                return portion

    def parse_text(self, text):
        # very similar to `Wordfuck`

        text = text.replace("\n", " ")

        operators = []
        cursor = 0
        while cursor < len(text):
            next_space = text.find(" ", cursor)
            if next_space == -1:
                next_space = len(text)

            word = text[cursor:next_space]
            repetitions_count = self.find_repetitions_count(word)

            operator_class = self.operator_remainder[repetitions_count]
            operator = operator_class(word, (cursor, next_space))
            operators.append(operator)

            cursor += (next_space - cursor) + 1

        return operators


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


class Wordfuck(Trivial, CustomCommand):
    """
    A trivial translation of BrainFuck. The specific characteristic is
    that any words are used as operators. The length of the word is used
    as a unique element.
    Space and line break are used as a separator, other characters are
    counted as part of the word. Words shorter than 2 or longer than 9
    characters are ignored.
    Matching:
    +---+---+
    | > | 6 |
    | < | 7 |
    | + | 4 |
    | - | 3 |
    | . | 2 |
    | , | 5 |
    | [ | 8 |
    | ] | 9 |
    +---+---+
    """

    operator_remainder = {
        6: Right,
        7: Left,
        4: Increment,
        3: Decrement,
        2: Output,
        5: Input,
        8: While,
        9: WhileEnd,
    }

    def parse_text(self, text):
        text = text.replace("\n", " ")

        operators = []
        cursor = 0
        while cursor < len(text):
            next_space = text.find(" ", cursor)
            if next_space == -1:
                next_space = len(text)

            word_len = next_space - cursor
            if 1 < word_len <= 9:
                word = text[cursor:next_space]
                operator_class = self.operator_remainder[word_len]
                operator = operator_class(word, (cursor, next_space))
                operators.append(operator)
            cursor += word_len + 1

        return operators


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

    def parse_text(self, text):
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
