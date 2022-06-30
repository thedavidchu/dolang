# Create test mem executable

# Make src visible to test
include_directories("${CMAKE_SOURCE_DIR}")

add_library("test_bool" "${CMAKE_SOURCE_DIR}/test/test_bool.c")
target_link_libraries("test_bool" PRIVATE "Unity")

# Main test executable
add_executable("test" "${CMAKE_SOURCE_DIR}/test/test.c")
target_link_libraries("test" PRIVATE "Unity" "test_bool")