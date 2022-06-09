# Create test mem executable
add_executable("test_mem" "${CMAKE_SOURCE_DIR}/unit-tests/test_mem.c")
target_link_libraries("test_mem" PRIVATE "common" "mem")