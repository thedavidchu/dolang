# Create the 'mem' target
add_library("mem" "${CMAKE_SOURCE_DIR}/mem/mem.c")

# Link executable to libraries
target_link_libraries("mem" PRIVATE "common")
