/* Recursive Fibonacci Sequence */
module io = import("stdio.h");

function fibonacci(n: i32) -> i32 {
    if n == 0 or n == 1 {
        return 1;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

function main() -> i32 {
    let result: i32 = fibonacci(10);
    /* I do not like copying the printf semantics from C... */
    io::printf("fibonacci(10) = %l\n", result);
    return 0;
}
