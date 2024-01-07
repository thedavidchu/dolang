/* Sum three numbers */
module io = import("stdio.h");

function sum_three(a: i32, b: i32, c: i32) -> i32 {
    return a + b + c;
}

function main() -> i32 {
    let sum: i32 = sum_three(1, 2, 3);
    io::printf("Sum should be 6: %d", sum);
    return 0;
}
