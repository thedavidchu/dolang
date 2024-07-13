from pathlib import Path

from compiler.error import LolError


def main():
    input_path = Path("examples/invalid/duplicate_function_names.lol")
    err = LolError(input_path, 96, 105, "duplicated function name")
    print(err)


if __name__ == "__main__":
    main()
