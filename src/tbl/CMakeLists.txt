# Create the 'tbl' target
add_library("tbl" "${CMAKE_SOURCE_DIR}/src/tbl/tbl.c")

# Link executable to libraries
target_link_libraries("tbl" PRIVATE "mem" "common" "arr")