"""
Add to list of used symbols (up to and including C99 standard).

TODO
----

1. Each symbol from C should have:
    a. its source,
    b. its type,
    c. etc.

    attached to make it easy to add to the symbol table.
"""
from enum import Enum, auto, unique
from typing import Dict

@unique
class SymbolSource(Enum):
    # C Language
    C_BUILTIN = auto()
    C_STDLIB = auto()
    C_STDIO = auto()
    # LOL
    LOL_BUILTIN = auto()
    # User
    USER = auto()


@unique
class CSymbolType(Enum):
    MACRO = auto()
    TYPE = auto()
    CONSTANT = auto()
    FUNCTION = auto()
    OTHER = auto()


################################################################################
### LANGUAGE KEYWORDS
################################################################################
_C89_KEYWORDS: Dict[str, SymbolSource] = {
    "auto": SymbolSource.C_BUILTIN,
    "break": SymbolSource.C_BUILTIN,
    "case": SymbolSource.C_BUILTIN,
    "char": SymbolSource.C_BUILTIN,
    "const": SymbolSource.C_BUILTIN,
    "continue": SymbolSource.C_BUILTIN,
    "default": SymbolSource.C_BUILTIN,
    "do": SymbolSource.C_BUILTIN,
    "double": SymbolSource.C_BUILTIN,
    "else": SymbolSource.C_BUILTIN,
    "enum": SymbolSource.C_BUILTIN,
    "extern": SymbolSource.C_BUILTIN,
    "float": SymbolSource.C_BUILTIN,
    "for": SymbolSource.C_BUILTIN,
    "goto": SymbolSource.C_BUILTIN,
    "if": SymbolSource.C_BUILTIN,
    "int": SymbolSource.C_BUILTIN,
    "long": SymbolSource.C_BUILTIN,
    "register": SymbolSource.C_BUILTIN,
    "return": SymbolSource.C_BUILTIN,
    "short": SymbolSource.C_BUILTIN,
    "signed": SymbolSource.C_BUILTIN,
    "sizeof": SymbolSource.C_BUILTIN,
    "static": SymbolSource.C_BUILTIN,
    "struct": SymbolSource.C_BUILTIN,
    "switch": SymbolSource.C_BUILTIN,
    "typedef": SymbolSource.C_BUILTIN,
    "union": SymbolSource.C_BUILTIN,
    "unsigned": SymbolSource.C_BUILTIN,
    "void": SymbolSource.C_BUILTIN,
    "volatile": SymbolSource.C_BUILTIN,
    "while": SymbolSource.C_BUILTIN,
}
_C99_KEYWORDS: Dict[str, SymbolSource] = {
    "inline": SymbolSource.C_BUILTIN,
    "restrict": SymbolSource.C_BUILTIN,
    "_Bool": SymbolSource.C_BUILTIN,
    "_Complex": SymbolSource.C_BUILTIN,
    "_Imaginary": SymbolSource.C_BUILTIN,
}
C_KEYWORDS = {**_C89_KEYWORDS, **_C99_KEYWORDS}


################################################################################
### LANGUAGE KEYWORDS
################################################################################
C_STDIO_KEYWORDS: Dict[str, SymbolSource] = {
    # According to https://www.tutorialspoint.com/c_standard_library/stdio_h.htm
    # Types
    "size_t": SymbolSource.C_STDIO,
    "FILE": SymbolSource.C_STDIO,
    "fpost_t": SymbolSource.C_STDIO,
    # Macros
    "NULL": SymbolSource.C_STDIO,
    "_IOFBF": SymbolSource.C_STDIO,
    "_IOLBF": SymbolSource.C_STDIO,
    "_IONBF": SymbolSource.C_STDIO,
    "BUFSIZ": SymbolSource.C_STDIO,
    "EOF": SymbolSource.C_STDIO,
    "FOPEN_MAX": SymbolSource.C_STDIO,
    "FILENAME_MAX": SymbolSource.C_STDIO,
    "L_tmpnam": SymbolSource.C_STDIO,
    "SEEK_CUR": SymbolSource.C_STDIO,
    "SEEK_END": SymbolSource.C_STDIO,
    "SEEK_SET": SymbolSource.C_STDIO,
    "TMP_MAX": SymbolSource.C_STDIO,
    "stderr": SymbolSource.C_STDIO,
    "stdin": SymbolSource.C_STDIO,
    "stdout": SymbolSource.C_STDIO,
    # Functions
    "fclose": SymbolSource.C_STDIO,
    "clearerr": SymbolSource.C_STDIO,
    "feof": SymbolSource.C_STDIO,
    "ferror": SymbolSource.C_STDIO,
    "fflush": SymbolSource.C_STDIO,
    "fgetpos": SymbolSource.C_STDIO,
    "fopen": SymbolSource.C_STDIO,
    "fread": SymbolSource.C_STDIO,
    "freopen": SymbolSource.C_STDIO,
    "fseek": SymbolSource.C_STDIO,
    "fsetpos": SymbolSource.C_STDIO,
    "ftell": SymbolSource.C_STDIO,
    "fwrite": SymbolSource.C_STDIO,
    "remove": SymbolSource.C_STDIO,
    "rename": SymbolSource.C_STDIO,
    "rewind": SymbolSource.C_STDIO,
    "setbuf": SymbolSource.C_STDIO,
    "setvbuf": SymbolSource.C_STDIO,
    "tmpfile": SymbolSource.C_STDIO,
    "tmpnam": SymbolSource.C_STDIO,
    "fprintf": SymbolSource.C_STDIO,
    "printf": SymbolSource.C_STDIO,
    "sprintf": SymbolSource.C_STDIO,
    "vfprintf": SymbolSource.C_STDIO,
    "vprintf": SymbolSource.C_STDIO,
    "vsprintf": SymbolSource.C_STDIO,
    "fscanf": SymbolSource.C_STDIO,
    "scanf": SymbolSource.C_STDIO,
    "sscanf": SymbolSource.C_STDIO,
    "fgetc": SymbolSource.C_STDIO,
    "fgets": SymbolSource.C_STDIO,
    "fputc": SymbolSource.C_STDIO,
    "fputs": SymbolSource.C_STDIO,
    "getc": SymbolSource.C_STDIO,
    "getchar": SymbolSource.C_STDIO,
    "gets": SymbolSource.C_STDIO,  # NOTE: very dangerous function!
    "putc": SymbolSource.C_STDIO,
    "putchar": SymbolSource.C_STDIO,
    "puts": SymbolSource.C_STDIO,
    "ungetc": SymbolSource.C_STDIO,
    "perror": SymbolSource.C_STDIO,
}

C_STDLIB_KEYWORDS = {
    # According to https://www.tutorialspoint.com/c_standard_library/stdlib_h.htm
    # Types
    "size_t": SymbolSource.C_STDLIB,
    "wchar_t": SymbolSource.C_STDLIB,
    "div_t": SymbolSource.C_STDLIB,
    "ldiv_t": SymbolSource.C_STDLIB,
    # Macros
    "NULL": SymbolSource.C_STDLIB,
    "EXIT_FAILURE": SymbolSource.C_STDLIB,
    "EXIT_SUCCESS": SymbolSource.C_STDLIB,
    "RAND_MAX": SymbolSource.C_STDLIB,
    "MB_CUR_MAX": SymbolSource.C_STDLIB,
    # Functions
    "atof": SymbolSource.C_STDLIB,
    "atoi": SymbolSource.C_STDLIB,
    "atol": SymbolSource.C_STDLIB,
    "strtod": SymbolSource.C_STDLIB,
    "strtol": SymbolSource.C_STDLIB,
    "strtoul": SymbolSource.C_STDLIB,
    "calloc": SymbolSource.C_STDLIB,
    "free": SymbolSource.C_STDLIB,
    "malloc": SymbolSource.C_STDLIB,
    "realloc": SymbolSource.C_STDLIB,
    "abort": SymbolSource.C_STDLIB,
    "atexit": SymbolSource.C_STDLIB,
    "exit": SymbolSource.C_STDLIB,
    "getenv": SymbolSource.C_STDLIB,
    "system": SymbolSource.C_STDLIB,
    "bsearch": SymbolSource.C_STDLIB,
    "qsort": SymbolSource.C_STDLIB,
    "abs": SymbolSource.C_STDLIB,
    "div": SymbolSource.C_STDLIB,
    "labs": SymbolSource.C_STDLIB,
    "ldiv": SymbolSource.C_STDLIB,
    "rand": SymbolSource.C_STDLIB,
    "srand": SymbolSource.C_STDLIB,
    "mblen": SymbolSource.C_STDLIB,
    "mbstowcs": SymbolSource.C_STDLIB,
    "mbtowc": SymbolSource.C_STDLIB,
    "wcstombs": SymbolSource.C_STDLIB,
    "wctomb": SymbolSource.C_STDLIB,
}
