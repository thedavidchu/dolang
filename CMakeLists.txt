####
#   # My Main CMake File
#
#   ## References
#   * Basic setup: https://raymii.org/s/tutorials/Cpp_project_setup_with_cmake_and_unit_tests.html
#   * Unity integration: https://www.poisel.info/posts/2019-07-15-cmake-unity-integration/
#   * Unity with CMake: http://www.throwtheswitch.org/build/cmake
####
   
cmake_minimum_required(VERSION 3.10)
project(CLib VERSION 0.0.0 LANGUAGES C)

# Setup Binary Executable Path
SET(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin)

# NOTE: I am developing with C99. Support for C90 will be potentially added
# later. The lack of printing size_t portably and portable fixed-width integers
# really bugged me.
set(C_COMPILER_VERSION c99 CACHE STRING "Compiler version")

if(C_COMPILER_VERSION STREQUAL c90)
    # Set ISO C90 standard
    message(FATAL_ERROR "I do not support C90 yet! Sorry <3 I love C90 too!")
    set(CMAKE_C_STANDARD 90)  # TODO(dchu) make compatible with both
elseif(C_COMPILER_VERSION STREQUAL c99)
    set(CMAKE_C_STANDARD 99)    # Allow // comments for debugging
else()
    message(FATAL_ERROR "Given C_COMPILER_VERSION unknown")
endif()

# Require a C-standard-compliant compiler
set(CMAKE_C_STANDARD_REQUIRED True)

# Make this directory public to tests
include_directories("${CMAKE_SOURCE_DIR}")

# Add libraries

# We declare a variable to select what to build set
SET(TARGET_GROUP "test" CACHE STRING "What Should I Build?")

if(TARGET_GROUP STREQUAL "release")
    # If we had any files that ONLY were compiled into our release, for example startup code,
    # it's really handy to put it here.
    message(FATAL_ERROR "I have not enabled release mode yet!")
elseif(TARGET_GROUP STREQUAL "test")
    # Show all warnings, warnings as errors, show where C90-non-compliant, debug
    set(CMAKE_C_FLAGS "-W -Wall -Werror -pedantic -g")

    # Our tests need to let CTest know we're running tests 
    include(CTest)

    # It also needs to understand we have code in source and test directories 
    add_subdirectory("${CMAKE_SOURCE_DIR}/test")
    add_subdirectory("${CMAKE_SOURCE_DIR}/third-party")
else() 
    message(FATAL_ERROR "I don't know the TARGET_GROUP you gave me!")
endif()

# Modules that exist in both our release and our unit tests, are added now
add_subdirectory("${CMAKE_SOURCE_DIR}/src")

