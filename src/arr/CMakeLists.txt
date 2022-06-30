# Create the 'arr' target
add_library("arr" "${CMAKE_SOURCE_DIR}/src/arr/arr.c")

# Link executable to libraries
target_link_libraries("arr" PRIVATE "mem" "common")