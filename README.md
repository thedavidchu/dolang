[![Linter](https://github.com/thedavidchu/dolang/workflows/Lint/badge.svg)](https://github.com/thedavidchu/dolang/actions)
[![Tester](https://github.com/thedavidchu/dolang/workflows/Test/badge.svg)](https://github.com/thedavidchu/dolang/actions)

The Do Language
================================================================================

Project Naming
--------------------------------------------------------------------------------

This language is named "Do" (as in "doe" a deer) because it is a C
transpiler and "do" is the name for "C" in the solfege system. It's short and
sweet. It looks like "do" as in the verb, which is perfect for an imperative
language. And rhymes with "go", a modern language that I admire (for its simplicity and resistance to feature creep). And best of all,
no other language is named "Do" as far as I know (unlike LOL/LOLCODE)! The only problem is that
the compiler would be named "doc". Well, if it's a transpiler, then we can call
it "dot". Finally, there are lots of musical puns to be had.

Historically, I played with the names "Object Zero" (.oz) and
"Light {Open-source,Object{ive,-oriented,}} Language". The former sounds silly;
the latter's acronym (.lol) is already used for the esoteric language, LOLCODE.

Project Goals
--------------------------------------------------------------------------------

1. Expose the internals of the transpiler to the user (if they so choose).
2. Provide a (1) secure, (2) usable, and (3) performant language, in that order.
3. Allow the programmer to dump as much information into the compiler as they wish.
How much is used by the compiler is another question. (Is this a good idea?)
4. Don't make silly features. 

Bootstrapping
--------------------------------------------------------------------------------

This project is to be bootstrapped in Python. Since it targets C, I can choose any 
language for the bootstrap. I chose Python because of its rich standard library,
and I am faster at writing Python than C.

For performance reasons, I have considered writing it in Rust. However, I am too far gone in Python (although I could do layer by layer).

Language Features
--------------------------------------------------------------------------------

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
- Inspired by Mur&phi;
  - Specificy ranges of numbers
  - I considered taking the operators (`=` for equality, `:=` for setting, etc) but I found it confusing even though I think it's logical from a non-C-family person)
