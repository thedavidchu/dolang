# Light Object-Oriented Language (LOL)

## Project Naming

I am trying to come up with an appropriate name for this project.
I like "Light Object Language" (because lol), but it's not really object-based.
Maybe "Light Open-Source Language" is better.
I was thinking of something short and close to the beginning of the alphabet (e.g.
"Ah").
I was musing with design objectives as well; my goals for this language are to be 
(1) secure, (2) usable, and (3) performant in that order (or maybe.
This would lead to the acronym "sup", like "wassup".
As a mature individual (the "lol" notwithstanding), I'm not sure if this would be 
great; it would also put my language in the middle-toward-the-end of the alphabet,
i.e. the most forgettable place ever.

## Project Goals

1. Expose the internals of the transpiler to the user (if they so choose).
2. Provide a (1) secure, (2) usable, and (3) performant language, in that order.
3. Allow the programmer to dump as much information into the compiler as they wish.
How much is used by the compiler is another question. (Is this a good idea?)
4. Don't make silly features. 

## Bootstrapping

This project is to be bootstrapped in Python. Since it targets C, I can choose any 
language for the bootstrap. I chose Python because of its rich standard library,
and I am faster at writing Python than C.

## Language Features

Make safety and usability/intuitiveness the priority. Then, performance can be 
added for a little extra work (since much of the optimization will be done on a 
small amount of the code).

- Drop in replacement for C
  - Structs are in order
  - Public functions, structs, etc. are linked with C
  - Initially, I will emit C code (and then maybe target LLVM-IR or some other compiler framework's IR)
- Ability to give compile-time information (in square brackets)
  - This can include ranges on integers (which must be proven at compile time or upon conversion, bound-checked at runtime)
- Inspired by Rust
  - Memory safety, immutability, "reserved" (in C's context) by default
  - Mark unowned data as "unowned"; otherwise, borrow check everything (but then lifetimes would be annoying to implement... how do they even work?)
  - Enum type for errors -- but we could use unused portions of integer/other ranges (see above, compile-time information)
  - Traits are cool
  - I like the fact there is no inheritance
- Inspired by Zig
  - No macros/preprocessor; compile-time running of any function
  - I like the idea of having the memory allocator specified--efficient allocation is a huge problem, so it would be cool to specify something with the "allocator trait", to use Rust's terminology
- Inspired by Python
  - Types can store methods--but maybe use the "::" syntax for any compile-time namespace stuff
    - E.g. `int16::max` -- I guess this is a language feature and not in keeping with putting things in the standard library
  - Have namespaces like Python, where you inherit the importing namespace's name
    - E.g. `import math; math.sqrt(10)` instead of C++'s `#include <cmath>\n std::sqrt`
    - I actually want to go further and use Nix's import syntax of `math = import("math");` or something... it's been a while since I wrote Nix
  - Python's constructor syntax makes more intuitive sense to me than C++'s
    - E.g. `x: ClassName = ClassName(arg0, arg1)` rather than `ClassName x(arg0, arg1);`. I just feel like the '=' makes everything clearer.
- Inspired by C
  - Limited language features
  - Optional standard library (I'll need to write wrappers for the C standard library)
  - By default, struct layouts are like in C (which I believe is in the order the user specified?)
  - Transparent what exactly is happening. No hidden function calls, no hidden operations (e.g. '<<' can be overloaded in C++)
  - Syntax is inspired by C-family
- Inspired by C++
  - Generics with templates. I'm going to use Python/Go's syntax
- Inspired by Java
  - The name "interface" instead of Rust's "trait" makes more sense to me... I may just be missing the full idea of Rust traits.
