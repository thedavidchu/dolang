/* Recursive Fibonacci Sequence */
module io = import("stdio.h");

function fibonacci(n: i32) -> i32 {
    if n == 0 {
        return 1;
    }
    if n == 1 {
        return 1;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

function main() -> i32 {
    let r0: i32 = fibonacci(0);
    let r1: i32 = fibonacci(1);
    let r2: i32 = fibonacci(2);
    let r3: i32 = fibonacci(3);
    let r4: i32 = fibonacci(4);
    let r5: i32 = fibonacci(5);
    let r6: i32 = fibonacci(6);
    let r7: i32 = fibonacci(7);
    let r8: i32 = fibonacci(8);
    let r9: i32 = fibonacci(9);
    let r10: i32 = fibonacci(10);
    /* I do not like copying the printf semantics from C... */
    io::printf("fibonacci(0..=10) = {%d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d}\n", r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10);
    return 0;
}
