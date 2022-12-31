"""
Another bicycle for generating tables.

Another one, but my own.
"""


__all__ = [
    "TableGenerator",
]


class Cell:
    """
    The class of a single table cell.
    It contains its data, split by lines, and values about the size of
    its data.
    """

    content: list[str]
    width: int
    height: int

    def __init__(self, data: str):
        content = str(data).splitlines()
        content = content or [""]
        content = list(map(
            lambda text: text.replace("\t", " ").rstrip().lstrip(),
            content
        ))

        self.content = content
        self.height = len(content)
        self.width = max(len(s) for s in content)

    _Sequence = str | list

    @staticmethod
    def sequence_to_size(sequence: _Sequence, size: int, null: _Sequence) -> _Sequence:
        """
        Symmetrically increases the sequence to the desired size by
        adding empty data from the ends.
        """

        length = len(sequence)
        last = (size - length) // 2
        first = last + (size - length) % 2
        return null * first + sequence + null * last

    def as_size(self, width: int, height: int) -> list[str]:
        """
        Fills in its data to the desired size, taking the form of a
        rectangle.
        """

        content = self.sequence_to_size(self.content, height, [""])
        content = [self.sequence_to_size(line, width, " ") for line in content]
        return content

    @property
    def flat_view(self) -> str:
        """
        Returns its value in one line.
        """
        return " ".join(self.content)


class TableGenerator:
    """
    Table generator class.
    Prints the table (in optionally the header and row names) in a
    formatted form.
    Focuses on working with string data, using a line break (\n) to split
    the data in one cell.
    """

    table: list[list[Cell]]
    widths: list[int]
    heights: list[int]
    row_separator: str
    cell_separator: list[str]

    def __init__(
            self,
            body: list[list],  # N rows x M cols
            header: list[str] = None,  # N-1/N vals
            params: list[str] = None,  # M vals
    ):
        self.table = self.generate_table(body, header, params)
        self.calculate_sizes()

    @staticmethod
    def generate_table(body, header, params) -> list[list[Cell]]:
        """
        It merges header, names and data into one table, checks for the
        correct size of the raw data, and converts everything to an
        internal representation (a list of Cells lists).
        """

        table = body  # size M x N -> [ [ cell x N ] x M ]

        # merging into one table
        if params:
            table = [[param] + row for (param, row) in zip(params, table)]
        if header:
            if table and len(header) == len(table[-1]) - 1:
                header = [""] + header
            table = [header] + table

        # checking for equal size
        M = len(table)
        if M == 0:
            raise ValueError("No data - table is empty!")
        N = len(table[0])
        is_same_length = all(len(row) == N for row in table)
        if not is_same_length:
            raise ValueError("Rows of the table have different lengths!")

        table = [
            [Cell(cell) for cell in row]
            for row in table
        ]
        return table

    def calculate_sizes(self) -> None:
        """
        Calculates the maximum height/width values for rows/columns (to
        fit all the data). Based on this, it creates a separator for rows
        and for columns.
        """

        self.widths = [
            max(cell.width for cell in column) + 2  # 2 - for cell margins
            for column in zip(*self.table)
        ]
        self.heights = [
            max(cell.height for cell in row)
            for row in self.table
        ]

        horizontal_cell_separators = ["-" * width for width in self.widths]
        self.row_separator = "+".join([""] + horizontal_cell_separators + [""])
        self.cell_separator = ["|"] * (len(self.widths) + 1)

    def generate(
            self,
            mark_header: bool = True,
            mark_params: bool = False
    ) -> str:
        """
        Generates a text representation of the table from its internal
        representation.
        Parameters allow you to enable highlighting (double lines) of the
        header and names.
        """

        def join_line(one_line_strings):
            """
            Connects the data in one line.
            """
            return cell_separator[0] + "".join(
                string + sep
                for (string, sep) in zip(one_line_strings, cell_separator[1:])
            )

        def generate_row(row: list[Cell], height) -> list[str]:
            """
            Generates a ready to print row from the list of cells (the
            internal representation of the row).
            """

            list_cells = [
                cell.as_size(width, height)
                for (cell, width) in zip(row, self.widths)
            ]
            list_strings = [
                join_line(one_line_strings)
                for one_line_strings in zip(*list_cells)
            ]

            return list_strings

        assert self.table, "No data - table is empty!"

        # create data for generate
        cell_separator = self.cell_separator.copy()
        row_separator = self.row_separator
        header_row_separator = row_separator

        if mark_params:
            cell_separator[0], cell_separator[1] = "||", "||"
            second_plus_index = row_separator[1:].index("+") + 1
            row_separator = (
                "+"
                + row_separator[:second_plus_index]
                + "+"
                + row_separator[second_plus_index:]
            )
            header_row_separator = row_separator

        if mark_header:
            header_row_separator = header_row_separator.replace("-", "=")

        # add header row
        table_strings: list[str] = (
            [header_row_separator]
            + generate_row(self.table[0], self.heights[0])
            + [header_row_separator]
        )

        # generate  rest of table
        for (row, height) in zip(self.table[1:], self.heights[1:]):
            table_strings += generate_row(row, height)
            table_strings += [row_separator]

        str_table = "\n".join(table_strings)
        return str_table

    def for_paste_view(self):
        """
        Returns a table that's useful for pasting into programs like
        Google Docs.
        The values are in one line and separated by tabulation, with the
        rows following each other.

        q\tw\te
        a\ts\td
        z\tx\tc
        """

        assert self.table, "No data - table is empty!"

        table_strings = [
            "\t".join(
                cell.flat_view for cell in row
            )
            for row in self.table
        ]
        str_table = "\n".join(table_strings)
        return str_table


if __name__ == "__main__":
    raw_header = ["Price / discount", "Description", "Is good"]
    raw_table = [
        [
            "watermelon",
            "$100 \n 5%",
            (
                "This is a very long \n"
                "description, it describes \n"
                "a watermelon"
            ),
            "Yes",
        ],
        [
            "melon",
            "$30 \n 10%",
            "Who even likes melons?",
            "No",
        ],
        [
            "apricot",
            "$65",
            (
                "Apricots are divided by 2, \n"
                "and then by 2 more, \n"
                "and then by 2 more, \n"
                "and then by 2 more, \n"
                "..."
            ),
            "Yes",
        ],
        [
            "pineapple",
            "$89",
            "Pen-pineapple-apple-pen!",
            "No",
        ],
        [
            "apple",
            "$123",
            "Pen-pineapple-apple-pen! \n (again?)",
            "Yes",
        ],
        [
            "pear",
            "$20 \n 15%",
            "The pear is terrible, \n let's burn them all!",
            "No",
        ],
        [
            "tangerine",
            "$43",
            "We shared a tangerine... \n oh no, it was an orange!",
            "Yes \n (for a bit)",
        ],
        [
            "orange",
            "$54",
            (
                "We shared an orange. \n"
                "There are many of us, but he is alone. \n"
                "This slice is for the hedgehog. \n"
                "This slice is for the swift. \n"
                "This slice is for ducklings. \n"
                "This slice is for kittens. \n"
                "This slice is for beaver. \n"
                "And for the wolf – the peel."
            ),
            "No",
        ],
        [
            "blueberry",
            "$55",
            "Why BLUEberry is called CHERnika?",
            "Yes",
        ],
    ]

    generator = TableGenerator(raw_table, header=raw_header)
    print(generator.generate(mark_params=True))
