from pathlib import Path


def get_line_and_column(text: str, position: int) -> tuple[int, int]:
    """
    Source: https://stackoverflow.com/questions/24495713/python-get-the-line-and-column-number-of-string-index
    """
    # NOTE  We start counting on line 1, so we add 1.
    # NOTE  A new line character ends the line, so we do not count the
    #       character itself in the count. I do not believe this
    #       implements this property.
    #       i.e. "Hello, World!\n"
    #            "Good-bye, World!\n"
    if not len(text):
        return 1, 1
    sp = text[: position + 1].splitlines(keepends=True)
    return len(sp), len(sp[-1])


def create_single_line_error_string(
    input_text: str, lineno: int, start_col: int, end_col: int, message: str
) -> str:
    text_lines: list[str] = input_text.splitlines()
    return (
        f"Error: {message}\n"
        f"> {lineno} | {text_lines[lineno-1]}\n"
        # NOTE  I just guessed for the number of spaces and '^'
        f"  {' ' * len(str(lineno))} | {' ' * (start_col-1)}{'^' * (end_col-start_col)}\n"
    )


def create_error_string(
    input_path: Path, start_position: int, end_position: int, message: str
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
    with input_path.open() as f:
        input_text: str = f.read()
    start_line, start_col = get_line_and_column(input_text, start_position)
    end_line, end_col = get_line_and_column(input_text, end_position)

    if start_line == end_line:
        return create_single_line_error_string(
            input_text, start_line, start_col, end_col, message
        )
    else:
        raise NotImplementedError
