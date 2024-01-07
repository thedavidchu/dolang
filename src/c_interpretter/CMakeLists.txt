# Make src public to tests
include_directories("${CMAKE_SOURCE_DIR}")

# Add libraries
## Compiler Compatibility Files
add_subdirectory("${CMAKE_SOURCE_DIR}/src/bool")
add_subdirectory("${CMAKE_SOURCE_DIR}/src/common")

## Standard Library Wrappers
add_subdirectory("${CMAKE_SOURCE_DIR}/src/mem")

## Custom Library
add_subdirectory("${CMAKE_SOURCE_DIR}/src/arr")
add_subdirectory("${CMAKE_SOURCE_DIR}/src/tbl")
add_subdirectory("${CMAKE_SOURCE_DIR}/src/rstr")

