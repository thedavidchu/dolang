# Create test mem executable

# Make src visible to test
include_directories("${CMAKE_SOURCE_DIR}")

add_executable("test_first" "${CMAKE_SOURCE_DIR}/src/main.c")
target_link_libraries("test_first" PUBLIC "common" "mem" "arr" "tbl" "rstr")
add_test(NAME "test_first" COMMAND "test_first")

add_executable("test_bool" "${CMAKE_SOURCE_DIR}/test/test_bool.c")
target_link_libraries("test_bool" PRIVATE "Unity")
add_test(NAME "test_bool" COMMAND "test_bool")

add_executable("test_mem" "${CMAKE_SOURCE_DIR}/test/test_mem.c")
target_link_libraries("test_mem" PRIVATE "Unity" "mem")
add_test(NAME "test_mem" COMMAND "test_mem")
