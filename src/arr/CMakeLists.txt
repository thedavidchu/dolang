# Create the 'arr' target
add_library("arr" "${CMAKE_SOURCE_DIR}/arr/arr.c")

# Link executable to libraries
target_link_libraries("arr" PRIVATE "mem" "common")