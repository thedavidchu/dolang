from pathlib import Path
from common import add_compiler_to_sys_path

add_compiler_to_sys_path()

from compiler.lol_error import LolError


def get_single_line_underlined_text(text: str):
    """
    NOTE    I assume the last line is the one that contains the underline."""
    errmsg, textmsg, underline = text.splitlines()
    return "".join([c for c, u in zip(textmsg, underline) if u == "^"])


def main():
    input_path = Path("examples/invalid/duplicate_function_names.lol")
    err = LolError(input_path, 96, 105, "duplicated function name")
    print(err)
    print(
        f"We should have underlined the following: {err.get_text_of_interest()}"
    )
    assert (
        get_single_line_underlined_text(err.error_string)
        == err.get_text_of_interest()
    )


if __name__ == "__main__":
    main()
