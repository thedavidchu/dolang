### Recursive Fibonacci Sequence
module io = import("stdio.h");

function fibonacci(n: int64) -> int64 {
    return fibonacci(n - 1) + fibonacci(n - 2);
}

function main() -> int64 {
    let result: int64 = fibonacci(10);
    # I do not like copying the printf semantics from C...
    io::stdout("fibonacci(10) = %l\n", result);
    return 0;
}
