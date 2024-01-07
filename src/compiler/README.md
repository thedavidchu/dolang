# Light Operational Language

Formerly `Light Object Language`, but then I decided that I wasn't going to use
OOP patterns.

## Intent

Create a transpiler that can rewrite a modern language to C.

There are many limiting things in C89 and C99 that can be made by a more
intelligent preprocessing step. This is it.

## Eventual Features

In no particular order, here are some fun features that I may add.

1. Generics.
2. Traits/Interfaces.
3. Lambdas/Closure. (???)
4. Borrow checker. (???)
5. Closures. (???)

## Future Ecosystem

1. VS Code extension with syntax highlighting.
2. Bootstrap this into its own language. What's nice is that once we write it,
it will generate C code so we can bootstrap it somewhat continuously (if you
know what I mean... I wasn't very clear).