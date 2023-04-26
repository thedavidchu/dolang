from lol_lexer_types import Token
from lol_parser_token_stream import TokenStream


def print_error(text: str, line_number: int, column_number: int):
    print(text.split("\n")[line_number - 1])
    print(" " * (column_number - 1) + "^")


def print_token_error(text: str, token: Token, error_msg: str) -> None:
    print(
        "--------------------------------------------------------------------------------"
    )
    print(
        f"Tokenization error on line "
        f"{token.line_number}, column {token.column_number}"
    )
    print(f"Error Message: {error_msg}")
    print("```")
    print_error(text, token.line_number, token.column_number)
    print("```")
    print(
        "--------------------------------------------------------------------------------"
    )
    return


def print_parser_error(stream: TokenStream, error_msg: str) -> None:
    text = stream.get_text()
    token = stream.get_token()
    print(
        "--------------------------------------------------------------------------------"
    )
    print(
        f"Parse error on line "
        f"{token.line_number}, column {token.column_number}"
    )
    print(f"Error Message: {error_msg}")
    print("```")
    print_error(text, token.line_number, token.column_number)
    print("```")
    print(
        "--------------------------------------------------------------------------------"
    )
    return
