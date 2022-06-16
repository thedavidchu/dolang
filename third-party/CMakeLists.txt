
# Tutorial: https://www.poisel.info/posts/2019-07-15-cmake-unity-integration/
add_library(Unity STATIC Unity-2.5.2 Unity/src/unity.c)
target_include_directories(Unity PUBLIC Unity/src)
