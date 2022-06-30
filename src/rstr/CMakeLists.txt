# Create the 'rstr' target
add_library("rstr" "${CMAKE_SOURCE_DIR}/src/rstr/rstr.c")

# Link executable to libraries
target_link_libraries("rstr" PRIVATE "common")