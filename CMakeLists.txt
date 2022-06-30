####
#   # My Main CMake File
#
#   ## References
#   * Basic setup: https://raymii.org/s/tutorials/Cpp_project_setup_with_cmake_and_unit_tests.html
#   * Unity integration: https://www.poisel.info/posts/2019-07-15-cmake-unity-integration/
####
   
cmake_minimum_required(VERSION 3.10)
project(CLib VERSION 0.0.0 LANGUAGES C)

set(C_COMPILER_VERSION c99 CACHE STRING "Compiler version")

if(C_COMPILER_VERSION STREQUAL c90)
    # Set ISO C90 standard
    set(CMAKE_C_STANDARD 90)  # TODO(dchu) make compatible with both
elseif(C_COMPILER_VERSION STREQUAL c99)
    set(CMAKE_C_STANDARD 99)    # Allow // comments for debugging
else()
    message(FATAL_ERROR "Given C_COMPILER_VERSION unknown")
endif()

# Require a C-standard-compliant compiler
set(CMAKE_C_STANDARD_REQUIRED True)

# Show all warnings, warnings as errors, show where C90-non-compliant, debug
set(CMAKE_C_FLAGS "-W -Wall -Werror -pedantic -g")

# Make this directory public to tests
include_directories("${CMAKE_SOURCE_DIR}")

# Add libraries
## Compiler Compatibility Files
add_subdirectory("${CMAKE_SOURCE_DIR}/src")
add_subdirectory("${CMAKE_SOURCE_DIR}/test")
add_subdirectory("${CMAKE_SOURCE_DIR}/third-party")
