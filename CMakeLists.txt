# This is the main CMake file

   
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
# set(CMAKE_C_STANDARD 90)  # TODO(dchu) make compatible with both
set(CMAKE_C_STANDARD 99)    # Allow // comments for debugging
set(CMAKE_C_STANDARD_REQUIRED True)

# Show all warnings, warnings as errors, show where C90-non-compliant, debug
set(CMAKE_C_FLAGS "-W -Wall -Werror -pedantic -g")

# Make src public to tests
include_directories("${CMAKE_SOURCE_DIR}")

# Add libraries
## Compiler Compatibility Files
add_subdirectory("${CMAKE_SOURCE_DIR}/src")
add_subdirectory("${CMAKE_SOURCE_DIR}/test")
add_subdirectory("${CMAKE_SOURCE_DIR}/third-party")
