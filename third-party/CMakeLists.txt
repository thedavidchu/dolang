add_library(Unity STATIC Unity-2.5.2 Unity/src/unity.c)
target_include_directories(Unity PUBLIC Unity/src)
