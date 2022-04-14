# Coding Style

## Definitions

* Integral Value: any `char`, `int`, `enum`, etc.

## Compiler Version
The code in this project should be as compatible with C89 as possible. This is
because C89 remains the best supported version of C (e.g. MSVC). The compiler
shall be called with `-std=c99 -pedantic -Wall -Werror` (ohhh, this pains me. I
wish I could ask you to use C89, but it is so limiting).

However, C99 has some nice-to-have features. I will admit that I really want to

* IO Functionality: `snprintf()` (get the number of characters used) and
`printf("%zu", (size_t)x);`
* Named Structure Tags: `struct point p = {.x = 0, .y = 0};`
* New Libraries: `<stdbool.h>` and `<inttypes.h>`
    * Make your own boolean library.
    * 
* Key Words: `inline`, `restrict`
    * In this project, `#define` them to empty strings if you are compiling
    wit C89.
* Variable initialization anywhere: `for (int i = 0; i < N; ++i) { ... }`
    * Try to avoid this in this project
* Calls with Structures: `f(((struct point){.x = 0, .y = 0}))`
    * Try to avoid this in this project
* C++ Style Comments: `// This is an inline comment`
    * Don't use this in this project.

Needless to say, some of these are excellent additions to the language.

## Portability
While passing or returning structures from functions is an established part of
the C89 language, the binary implementation is compiler-dependent. While some
compilers may use registers, others may use memory. For this reason, we will
not pass structures between functions, but rather pass _pointers_ to structures.

Strictly speaking, external identifiers in C89 are only guaranteed to be
significant to 6 characters; internal identifiers are only guaranteed to be
significant to 31 characters. We will ignore this. This is simply a matter of
refactoring the code.

## Safety Conventions

### Initialization
All invalid pointers shall be set to NULL. My `mem_malloc()` function will
actually enforce this. Where difficulty with this arises is if we allocate a
structure containing pointers, but the structure has non-null pointers. It is
the user's job to set all these pointers to NULL as soon as the memory is
allocated. The function `mem_malloc()` does not do this.

All numeric values shall be set to `0`.

All structures shall be initialized using `{ 0 }`

### Bracing
All groups of code shall be braced (including no code). I believe this is inline
with MISRA's standard.

```c
while (x-- > 0) {
    /* no op */
}
```

Yes, I know that you can put a semicolon at the end of the while statement. But
don't.


### Switch Statements
Switch statements should not have fall-through unless it is explicitly marked.
Moreover, every instance should have a default, even if it is impossible. If it
is deemed impossible to hit the default, then an assertion should be thrown.

### Increasing Integral Values
For any of the operators that grow an integral value, the bounds must be checked
before an operator. These include `x + y`, `x << y`, and `x * y`. An idiom to
check the validity of these operators is to apply them, then apply the inverse,
before checking for equality.

E.g. `x == (x + y) - y` implies a valid addition.

It is for this reason that my memory functions take in two arguments, so that
the user does not have to check the bounds on multiplication themselves.

Admittedly, the `++i` or `i++` operators can overflow. However, we will ignore
this fact for now. In a for-loop, they are checked upon every iteration.

### Division
A check for zero must be performed before doing any division operation. These
include `x / y` and `x % y`.

### Right Bit Shifting with Signed Integrals
Don't right bit shift with signed integrals. The implementation is compiler-
specific with regard to the sign extension.

Or at the very least, never do this with a negative signed integral. If I
remember correctly, positive signed integrals behave like unsigned integrals for
right bit shifts.

### Bitwise Operation Ordering
The order of bitwise operations is implementation defined. There is no short-
circuit logic, unlike logical boolean operations.

### Side Effects in Function Calls
No function call may use arguments with side-effects.

At the very least, do not rely on a particular order of side-effects when
calling a function. All of the side-effects will take place before the called
function is entered, however the order is compiler dependent.

### Strings
Unless the string appears directly as a `"<this is a string>"` in the code, do
not rely on it being null-terminated. Especially not if you used a copy to a
buffer. Unless you explicity copy in a null character at the end.

Where possible, store the length of a string along with the string.

Do not use unsafe standard library functions that rely on strings to be null-
terminated. Only use ones that have a known number of bytes to operate upon.


## Conventions

### Braces and If-Else Chains
The structure of braces shall follow K&R. The braces for functions shall follow
this pattern (contrary to K&R's usage).

```c
int function(int x, int y) {
    if (x) {
        /* ... */
    } else if (y) {
        /* ... */
    } else {
        /* ... */
    }
}
```

### Labels and Switches
Labels shall be indented 1 less than the surrounding code.

```c
int function(int x) {
    switch (x) {
    case 0:
        /* ... */
    case 1:
        /* ... */
    case 2:
        /* ... */
    default:
        /* ... */
    }

    goto cleanup:

cleanup:
    /* ... */
}
```

### Use of Assertions
Use assertions for code where it is impossible to get to somewhere. Otherwise,
use a return statement for ease of testing. This means that assertions can be
used liberally for commenting.
