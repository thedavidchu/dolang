/* A simple program to demonstrate recursion */
module io = import("stdio.h");

function nested_if(x: i32, y: i32) -> i32 {
    if x == 0 {
        if y == 0 {
            io::printf("Both x and y are zero!\n");
        } else {
            io::printf("x is zero but y is %d\n", y);
        }
    } else {
        if y == 0 {
            io::printf("x is %d but y is zero\n", x);
        } else {
            io::printf("x is %d and y is %d\n", x, y);
        }
    }

    /* NOTE I cannot return void because my compiler treats it as a regular type */
    return 0;
}

function main() -> i32 {
    nested_if(0, 0);
    nested_if(0, 1);
    nested_if(1, 0);
    nested_if(1, 1);
    return 0;
}
