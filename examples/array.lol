/* Demonstrate array syntax */
module io = import("stdio.h");

function main() -> i32 {
    let array: Array[i32] = [0, 1, 2, 3];
    io::printf("Array: [%d, %d, %d, %d]\n",
               array[0], array[1], array[2], array[3]);
    return 0;
}
