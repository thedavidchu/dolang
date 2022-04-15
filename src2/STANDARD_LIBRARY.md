# Using the Standard Library

This file follows the structure of **Appendix B** in Brian Kernighan and Dennis
Ritchie's _The C Programming Language, Edition 2_ (i.e. "K&R"), which itself is
based on the C89/90 Standard.

Large sections were copied verbatim with the understanding that the sections
were taken from the Standard.

An idiom that we will use for standard library calls is as follows:

```c
if (errno) {
    return errno;
}
/* $r is the status or error condition */
if (/* error condition in standard library call */) {
    assert(errno && "errno not set upon standard library error!"); /* if applicable */
    /* DO CLEAN UP HERE */
    return errno;
}
assert (errno == 0 && "errno set upon no error!");
/* CONTINUE OTHER WORK HERE */
```

Take an example using the standard library function, `calloc`.

```c
int r = 0;
int *ptr = NULL;

if (errno) {
    return errno;
}
if (N && (ptr = calloc(N, sizeof *ptr)) == NULL) {
    assert(errno == ENOMEM && "errno not set upon calloc error!");
    /* No cleanup required here */
    return errno;
}
/* CONTINUE OTHER WORK HERE */
```

## Contents

1. Input and Output (`<stdio.h>`)
2. Character Class Tests (`<ctype.h>`)
3. String Functions (`<string.h>`)
4. Mathematical Functions (`<math.h>`)
5. Utility Functions (`<stdlib.h>`)
6. Diagnostics (`<assert.h>`)
7. Variable Argument Lists (`<stdarg.h>`)
8. Non-Local Jumps (`<setjmp.h>`)
9. Signals (`<signal.h>`)
10. Date and Time Functions (`<time.h>`)
11. Implementation-Defined Ingegral Limits (`<limits.h`>)
12. Implementation-Defined Floating-Point Limits (`<float.h`>)


## Input and Output (`<stdio.h>`)

### File Operations
Function | Description
:--------|:---------------------------------------------------------------------
`FILE *fopen(const char *filename, const char *mode)`                   |
`FILE *freopen(const char *filename, const char *mode, FILE *stream)`   |
`int fflush(FILE *stream)`                                              |
`int fclose(FILE *stream)`                                              |
`int remove(const char *filename)`                                      |
`int rename(const char *oldname, const char *newname)`                  |
`FILE *tmpfile(void)`                                                   |
`char *tmpname(chars[L_tmpnam])`                                        |
`int setvbuf(FILE *stream, char *buf, int mode, size_t size)`           |
`void setbuf(FILE *stream, char *buf)`                                  |

### Formatted Output
Function                                                    | Description
:-----------------------------------------------------------|:------------------
`fprintf(FILE *stream, const char *format, ...)`            |
`printf(const char *format, ...)`                           |
`sprintf(char *s, const char *format, ...)`                 |
`vfprintf(FILE *stream, const char *format, va_list arg)`   |
`vprintf(const char *format, va_list arg)`                  |
`vsprintf(char *s, const char *format, va_list arg)`        |


### Formatted Input
Function                                            | Description
:---------------------------------------------------|:--------------------------
`int fscanf(FILE *stream, const char *format, ...)` |
`int scanf(const char *format, ...)`                |
`int sscanf(char *s, const char *format, ...)`      |

### Character Input and Output Functions/Macros
Function                                    | Description
:-------------------------------------------|:----------------------------------
`int fgetc(FILE *stream)`                   |   return the next character of a stream (`unsigned char`) or `EOF` if an error occurs
`char *fgets(char *s, int n, FILE *stream)` |   gets at most the nex `n-1` characters, stopping upon a newline, which is included in the array. A `'\0'` is included at the end. Returns `s`, or `NULL` upon error.
`int fputc(int c, FILE *stream)`            |   writes `c` as an `unsigned char` onto the `stream`. Returns `c`, or `EOF` upon error.
`int fputs(const char *s, FILE *stream)`    |   writes the string `s` (doesn't necessarily contain `'\n'`) on `stream`. Returns non-negative, or `EOF` upon error.
`int getc(FILE *stream)`                    |   equivalent to `fgetc`, except it may be implemented as a macro (thus evaluating `stream` twice).
`int getchar(void)`                         |   equivalent to `getc(stdin)`.
`char *gets(char *s)`                       |   reads the next input line into `s`, replacing the `'\n'` with `'\0'`. Returns s, or `NULL` upon end-of-file or error.
`int putc(int c, FILE *stream)`             |   equivalent to `fputc`, except it may be implemented as a macro (thus evaluating `stream` twice).
`int putchar(int c)`                        |   equivalent to `putc(c, stdout)`.
`int puts(const char *s)`                   |   
`int ungetc(int c, FILE *stream)`           |   pushes `c` (converted to `unsigned char`) back onto the stream whence it came. It will be returned on the next read. Only one character of pushback is guaranteed per stream. `EOF` may not be pushed back. Returns the pushed back character, or `EOF` upon error.

### Direct Input and Output Functions
I am not entirely sure what these functions do.

Function                                                                | Description
:-----------------------------------------------------------------------|:------
`size_t fread(void *ptr, size_t size, size_t nobj, FILE *stream)`       |
`size_t fwrite(const void *ptr, size_t size, size_t nobj, FILE *stream)`|

### File Positioning
Function                                            | Description
:---------------------------------------------------|:--------------------------
`int fseek(FILE *stream, long offset, int origin)`  |
`long ftell(FILE *stream)`                          |
`void rewind(FILE *stream)`                         |
`int fgetpos(FILE *stream, fpos_t *ptr)`            |
`int fsetpos(FILE *stream, const fpos_t *ptr)`      |

### Error Functions
Function                        | Description
:-------------------------------|:----------------------------------------------
`void clearerr(FILE *stream)`   | clears end-of-file and error indicators for the stream.
`int feof(FILE *stream)`        | returns non-zero if the end-of-file indicator for stream is set.
`int ferror(FILE *stream)`      | returns non-zero if the error indicator for stream is set.
`void perror(const char *s)`    | `fprintf(stderr, "%s: %s\n", s, "<error-message>")`, c.f. `strerror`.


## Character Class Tests (`<ctype.h>`)

### Character Testing
The argument `c` is an `int` that is either `EOF` or representable as an
`unsigned char`. The return value is an `int`; non-zero denotes _true_, while
zero denotes _false_.

Function        | Description
:---------------|:--------------------------------------------------------------
`isalnum(c)`    | letter or digit character. Implies that `isalpha(c) || isdigit(c)` is true.
`isalpha(c)`    | letter character. Implies that `isupper(c) || islower(c)` is true.
`iscntrl(c)`    | control character.
`isdigit(c)`    | digit character.
`isgraph(c)`    | printing character (excluding space).
`islower(c)`    | lower-case letter.
`isprint(c)`    | printing character (including space).
`ispunct(c)`    | printing character (excluding space, letter, digit).
`isspace(c)`    | space, formfeed, newline, carriage return, tab, vertical tab.
`isupper(c)`    | upper-case letter.
`isxdigit(c)`   | hexadecimal digit.

### Conversions
Function        | Description
:---------------|:--------------------------------------------------------------
`int tolower(c)`| convert `c` to lower-case.
`int toupper(c)`| convert `c` to upper-case.


## String Functions (`<string.h>`)

### Null-Terminated Character String Functions
The arguments `s` and `t` are of type `char *`; the arguments `cs` and `ct` are
of type `const char *`; and the argument `n` is of type `size_t`.

String Function             | Description
:---------------------------|:--------------------------------------------------
`char *strcpy(s, ct)`       | do not use.
`char *strncpy(s, ct, n)`   | confusing, do not use (may not null-terminate?).
`char *strcat(s, ct)`       |
`char *strncat(s, ct, n)`   | confusing, do not use (may not null-terminate?).
`int strcmp(cs, ct)`        |
`int strncmp(cs, ct, n)`    |
`char *strchr(cs, c)`       |
`char *strrchr(cs, c)`      |
`size_t strspn(cs, ct)`     |
`size_t strcspn(cs, ct)`    |
`char *strpbrk(cs, ct)`     |
`char *strstr(cs, ct)`      | 
`size_t strlen(cs)`         | returns the length of a string, not including the terminating `'\0'`.
`char *strerror(n)`         | returns an implementation-dependent error message about error n.
`char *strtok(s, ct)`       | confusing, do not use.

### Raw Memory Functions

The arguments `s` and `t` are of type `void *`; the arguments `cs` and `ct` are
of type `const void *`; the argument `n` is of type `size_t`; and the argument
`c` is of type `int` representable as an `unsigned char`.

Memory Function             | Description
:---------------------------|:--------------------------------------------------
`void *memcpy(s, ct, n)`    | copy `n` characters from `ct` to `s`. Return `s`.
`void *memmove(s, ct, n)`   | same as `memcpy`, but `s` and `ct` may overlap. Return `s`.
`int memcmp(cs, ct, n)`     | compare `cs` and `ct`. Return -1 if `cs < ct`; 0 if `cs == ct`; and +1 if `cs > ct`.
`void *memchr(cs, c, n)`    | return a pointer to the first occurence of `c` in `cs` or `NULL` if `c` is not in the first `n` characters of `cs`.
`void *memset(s, c, n)`     | place character `c` into the first `n` characters of `s`. Return `s`.

## Mathematical Functions (`<math.h>`)

### Important Macros

* `HUGE_VAL`: a positive `double` value.
* `EDOM`    : from `<errno.h>`. A _domain error_ has occurred (i.e. the argument
              is outside the bounds of the allowable domain for the function).
              Upon a _domain error_, `errno` is set to `EDOM`; the return value
              of the function is implementation-dependent.
* `ERANGE`  : from `<errno.h>`. A _range error_ has occurred. (i.e. the result
              is outside the bounds of the representable range of a `double`).
              Upon overflow, the function returns `HUGE_VAL` is returned with
              the correct sign and `errno` is set to `ERANGE`; upon underflow,
              the function returns 0 and `errno` being set to `ERANGE` is
              implementation-dependent.

### Error Checking

Error checking should be done as specified by the common idiom. For example, a 

```c
double r = 0.0;

if (errno != 0) {
    return errno;
}
r = exp(x);
/* Check for out-of-domain error before we check that the return is in the
correct range, because the return is implementation-dependent upon a domain
error, so we cannot guarantee that it will be in the valid range. */
if (errno == EDOM) {
    return EDOM;
}

assert(r >= 0.0 && "illegal value for exponent!");
/* Overflow */
if ((r == HUGE_VAL /* we do not check for -HUGE_VAL because it must be positive according to the assertion */) && errno == ERANGE) {
    return EDOM;
} else if (r == 0.0 && errno == ERANGE) {
    return EDOM;
} else {
    /* ok */
}
```

### Functions

The arguments `x` and `y` are of type `double`; the argument `n` is of type
`int`. All functions return a `double`.

Function                | Description
:-----------------------|:------------------------------------------------------
`sin(x)`                | sine of `x`.
`cos(x)`                | cosine of `x`.
`tan(x)`                | tangent of `x`.
`asin(x)`               | arcsine of `x` in range [`-\pi/2`, `\pi/2`], `x \epsilon [-1, 1]`.
`acos(x)`               | arccosine of `x` in range [`0`, `\pi`], `x \epsilon [-1, 1]`.
`atan(x)`               | arctangent of `x` in range [`-\pi/2`, `\pi/2`].
`atan(y, x)`            | arctangent of (`y/x`) in range [`-\pi`, `\pi`].
`sinh(x)`               | hyperbolic sine of x.
`cosh(x)`               | hyperbolic cosine of x.
`tanh(x)`               | hyperbolic tangent of x.
`exp(x)`                | natural exponential function `e^x`.
`log(x)`                | natural logarithm `ln(x)`, x > 0.
`log10(x)`              | base-10 logarithm `log_10(x)`, x > 0.
`pow(x, y)`             | `x^y`. A domain error occurs if `x = 0` and `y <= 0`, or if `x < 0` and y in not an integer.
`sqrt(x)`               | square root of `x`, `x >= 0`.
`ceil(x)`               | returns an integer no less than `x` as a double.
`floor(x)`              | returns an integer no greater than `x` as a double.
`fabs(x)`               | absolute value of `x`
`ldexp(x, n)`           | `x * 2^n`
`frexp(x, int *exp)`    | no clue
`modf(x, double *ip)`   | splits `x` into the integer and fractional parts. 
`fmod(x, y)`            | floating-point remainder of `x/y`, with 

## Utility Functions (`<stdlib.h>`)

Function                                                        | Description
:---------------------------------------------------------------|:--------------
`double atof(const char *s)`                                    | equivalent to `strtod(s, (char **)NULL)`.
`int atoi(const char *s)`                                       | equivalent to `(int)strtol(s (char **)NULL, 10)`.
`long atol(const char *s)`                                      | equivalent to `strtol(s, (char **)NULL, 10)`.
`double strtod(const char *s, char **endp)`                     | return `double` with unprocessed characters starting at `endp`.
`long strtol(const char *s, char **endp, int base)`             | return `long` with unprocessed characters starting at `endp`. The `base` from 2 to 36 uses 0, 1, ... 9, a/A, bB, ..., z/Z. A base of 0 means the function will parse the value as a decimal, octal (starting with `0...`), or hexadecimal (starting with `0x...`).
`unsigned long strtoul(const char *s, char **endp, int base)`   | return `unsigned long` version of `strtol`.

### Pseudo Random Numbers
Function                        | Description
:-------------------------------|:----------------------------------------------
`int rand(void)`                | returns a pseudo-random integer in the range 0 to `RAND_MAX`, which is at least 32767
`void srand(unsigned int seed)` | sets the seed for pseudo-random generator.

### Memory Allocation
Function                                | Description
:---------------------------------------|:--------------------------------------
`void *calloc(size_t nobj, size_t size)`| memory.
`void *malloc(size_t size)`             | memory.
`void *realloc(void *p, size_t size)`   | memory.
`void free(void *p)`                    | memory.

### Exiting
Function                        | Description
:-------------------------------|:----------------------------------------------
`void abort(void)`              |
`void exit(int status)`         |
`int atexit(void (*fcn)(void))` | run `fcn` upon exit (in reverse order).

### System Interactions
Function                        | Description
:-------------------------------|:----------------------------------------------
`int system(const char *s)`     |
`char *getenv(const char *name)`|

### Array Sorting and Searching
Function                                                        | Description
:---------------------------------------------------------------|:--------------
`void *bsearch(const void *key, const void *base, size_t n, size_t size, int(*cmp)(const void *keyval, const void *datum))` |
`void qsort(void *base, size_t n, size_t size, int (*cmp)(const void *, const void *))` |

### Miscellaneous Math Functions
Function                            | Description
:-----------------------------------|:------------------------------------------
`int abs(int n)`                    |
`long labs(long n)`                 |
`div_t div(int num, int denom)`     | compute the quotient and remainder of `num/denom`. Returns a `div_t = {.quot = $quotient, .rem = $remainder}`.
`ldiv_t ldiv(long num, long denom)` |


## Diagnostics (`<assert.h>`)

Function                | Description
:-----------------------|:------------------------------------------------------
`assert(expression)`    | tests the expression. Upon failure, prints `Assertion failed: $expression, file $__FILE__, line $__LINE__` to `stderr` and aborts. Assertions are ignored if the macro `NDEBUG` is defined when `<assert.h>` is included.

## Variable Argument Lists (`<stdarg.h>`)

```c
/* Declare a `va_list` that will point to each successive argument. */
va_list ap;
/* Initialize `ap` to point to the first argument. */
va_start(va_list ap, $last_argument);
/* Get the next argument in the list. How does this signal the last element? */
$type va_arg(va_list ap, $type);
/* Clean up the `va_list` when we are done with the arguments and before we
return from our current function.  Returns void. */
va_end(va_list ap);
```

## Non-Local Jumps (`<setjmp.h>`)

Non-local jumps are useful for escaping deeply nested functions. That said, I
will not use them in this project.

Function                            | Description
:-----------------------------------|:------------------------------------------
`int setjmp(jmp_buf env)`           | save the state in `env` and return zero the first time we call it. Upon a jump back, this will return a non-zero value. This can only legally occur in an `if`, `switch`, or loop-condition.
`void longjmp(jmp_buf env, int val)`| restores the state saved by the most recent `setjmp`. Note

```c
if (setjmp(env) == 0) {
    /* execute on direct call */
} else {
    /* execute after calling longjump */
}
```

## Signals (`<signal.h>`)

This library deals with handling runtime exceptions. It is confusing, so I will
not use it for now. I do, however, admit that this may be interesting for a more
advanced C programmer.

## Date and Time Functions (`<time.h>`)

This library helps with manipulating dates and times. I will not enumerate the
details because I believe it is a little bit silly. Well, not silly. But a bit
arbitrary.

## Implementation-Defined Ingegral Limits (`<limits.h`>)

This library defines a set of macros detailing various limits. Those I provide,
as in the reference manual, are the minimum allowable values (although, I
believe the `char` type is limited to 8 bits); thus the values may be greater.

Macro       |   Value (2's Complement)      | Description
:-----------|------------------------------:|:----------------------------------
`CHAR_BIT`  |   8                           | bits in a `char`
`CHAR_MAX`  |   `UCHAR_MAX` or `SCHAR_MAX`  | maximum value of `char`
`CHAR_MIN`  |   `0` or `SCHAR_MIN`          | minimum value of `char`
`INT_MAX`	|   +32767                      | maximum value of `int`
`INT_MIN`	|   -32767 (-32768)             | minimum value of `int`
`LONG_MAX`  |   +2147483647                 | maximum value of `long`
`LONG_MIN`  |   -2147483647 (-2147483648)   | minimum value of `long`
`SCHAR_MAX` |   +127                        | maximum value of `signed char`
`SCHAR_MIN` |   -127 (-128)                 | minimum value of `signed char`
`SHRT_MAX`  |   +32767                      | maximum value of `short`
`SHRT_MIN`  |   -32767 (-32768)             | minimum value of `short`
`UCHAR_MAX` |   255                         | maximum value of `unsigned char`
`UINT_MAX`  |   65535                       | maximum value of `unsigned int`
`ULONG_MAX` |   4294967295                  | maximum value of `unsigned long`
`USHRT_MAX` |   65535                       | maximum value of `unsigned short`

## Implementation-Defined Floating-Point Limits (`<float.h`>)

This library provides macros dealing with floating-point numbers. The following
are a subset of those available, as in the reference text.

Macro           | Value     | Description
:---------------|----------:|:--------------------------------------------------
FLT_RADIX       | 2         | radix of exponent representation (e.g. 2, 16).
FLT_ROUNDS      |           | floating-point rounding mode for addition.
FLT_DIG         | 6         | decimal digits of precision.
FLT_EPSILON     | 1E-5      | smallest number `x` such that `1.0 + x != 1.0`.
FLT_MANT_DIG    |           | number of base `FLT_RADIX` digits in mantissa.
FLT_MAX         | 1E+37     | maximum floating-point number.
FLT_MAX_EXP     |           | maximum `n` such that `FLT_RADIX^n-1` is representable.
FLT_MIN         | 1E-37     | minimum normalized floating-point number.
FLT_MIN_EXP     |           | minimum n such that `10^n` is a normalized number.
DBL_DIG         | 10        | decimal digits of precision.
DBL_EPSILON     | 1E-9      | smallest number `x` such that `1.0 + x != 1.0`.
DBL_MANT_DIG    |           | number of base `FLT_RADIX` digits in mantissa.
DBL_MAX         | 1E+37     | maximum `double` floating-point number.
DBL_MAX_EXP     |           | maximum `n` such that `FLT_RADIX^n-1` is representable.
DBL_MIN         | 1E-37     | minimum normalized `double`floating-point number.
DBL_MIN_EXP     |           | minimum `n` such that `10^n` is a normalized number.
