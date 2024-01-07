/* Sum three numbers */
module io = import("stdio.h");

function math_operation(a: i32, b: i32, c: i32, d: i32) -> i32 {
    return
        a + b * c + d
        + a * (b + c) * d;
}

function main() -> i32 {
    let sum: i32 = math_operation(1, 2, 3, 4);
    io::printf("Sum should be 31: %d\n", sum);
    return 0;
}