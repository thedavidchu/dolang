####
#   # My CMake File
#
#   ## References
#   * https://raymii.org/s/tutorials/Cpp_project_setup_with_cmake_and_unit_tests.html
####
cmake_minimum_required(VERSION 3.10)

# Project Name
project(CLib VERSION 0.0.0 LANGUAGES C)

# Set ISO C90 standard
set(CMAKE_C_STANDARD 90)
set(CMAKE_C_STANDARD_REQUIRED True)

# Show all warnings, warnings as errors, show where C90-non-compliant, debug
set(CMAKE_C_FLAGS "-Wall -Werror -pedantic -g")

# Make src public to tests
include_directories("${CMAKE_SOURCE_DIR}")

# Add libraries
add_subdirectory("${CMAKE_SOURCE_DIR}/mem")

# Create executable
add_executable("main" "${CMAKE_SOURCE_DIR}/main.c")

# Link executable to libraries
target_link_libraries("main" PUBLIC "mem")
