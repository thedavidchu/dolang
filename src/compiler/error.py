from pathlib import Path


class LolError:
    def __init__(
        self,
        input_: Path | str,
        start_position: int,
        end_position: int,
        message: str,
    ):
        self.error_string = LolError.create_error_string(
            input_, start_position, end_position, message
        )

        self.input_ = input_
        self.start_position = start_position
        self.end_position = end_position
        self.message = message

    def __str__(self) -> str:
        return self.error_string

    def __repr__(self) -> str:
        return self.error_string

    @staticmethod
    def print_error(
        input_: Path | str,
        start_position: int,
        end_position: int,
        message: str,
    ):
        error_string = LolError.create_error_string(
            input_, start_position, end_position, message
        )
        print(error_string)

    def get_text_of_interest(self) -> str:
        """
        @brief  This function returns the text that we intended to highlight.

        @note   This intention of this function is for debugging.
        """
        with self.input_.open() as f:
            text = f.read()

        return text[self.start_position : self.end_position]

    @staticmethod
    def get_position(text: str, lineno: int, colno: int) -> tuple[int, int]:
        # We want to take the first 'lineno' lines (i.e. we want a list
        # of length 'lineno' lines).
        lines = text.splitlines()[: lineno + 1]
        assert len(lines) == lineno
        # Similarly, we want the line of interest (i.e. the last line)
        # to be a string of 'colno' characters.
        lines[-1] = lines[-1][: colno + 1]
        assert len(lines[-1]) == colno
        return len("\n".join(lines))

    @staticmethod
    def get_line_and_column(text: str, position: int) -> tuple[int, int]:
        """
        @note   I index from zero.
        Source: https://stackoverflow.com/questions/24495713/python-get-the-line-and-column-number-of-string-index
        """
        # NOTE  A new line character ends the line, so we do not count the
        #       character itself in the count. I do not believe this
        #       implements this property.
        #       i.e. "Hello, World!\n"
        #            "Good-bye, World!\n"
        if not len(text):
            return 0, 0
        sp = text[:position].splitlines()
        lineno, colno = len(sp) - 1, len(sp[-1])
        return lineno, colno

    @staticmethod
    def create_single_line_error_string(
        input_text: str, lineno: int, start_col: int, end_col: int, message: str
    ) -> str:
        """Create an error string for an error that spans a single line."""
        text_lines: list[str] = input_text.splitlines()
        user_line = lineno + 1
        return (
            f"> Error: {message}\n"
            f"> {user_line} | {text_lines[lineno]}\n"
            # NOTE  I just guessed for the number of spaces and '^'
            f"> {' ' * len(str(user_line))} | {' ' * (start_col)}{'^' * (end_col-start_col)}\n"
        )

    @staticmethod
    def create_error_string(
        input_: Path | str,
        start_position: int,
        end_position: int,
        message: str,
    ) -> str:
        """
        @brief  Create a string with the error underlined and the error message displayed.

        @param  start_position: int
                    The very first character that should be highlighted.
        @param  end_position: int
                    One past the last character that should be highlighted.

        @example
        > Error: Expecting expression, got '{'
        > 10    |
        > 11    | if {
        >            ^
        > 12    |     io::printf("Hello, World!\n");
        > 13    | }
        >
        """
        assert start_position < end_position

        if isinstance(input_, Path):
            with input_.open() as f:
                input_text: str = f.read()
        elif isinstance(input_, str):
            input_text = input_
        start_line, start_col = LolError.get_line_and_column(
            input_text, start_position
        )
        end_line, end_col = LolError.get_line_and_column(
            input_text, end_position
        )

        if start_line == end_line:
            return LolError.create_single_line_error_string(
                input_text, start_line, start_col, end_col, message
            )
        else:
            raise NotImplementedError
