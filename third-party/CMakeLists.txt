
# Tutorial: https://www.poisel.info/posts/2019-07-15-cmake-unity-integration/
add_library("Unity" STATIC "${CMAKE_SOURCE_DIR}/third-party/Unity-2.5.2/src/unity.c")
target_include_directories("Unity" PUBLIC "Unity-2.5.2/src")
