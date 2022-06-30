#!/bin/bash

# This file is to test and run the 
rm ./cmake/src/main ./cmake/test/test;
cmake --build ./cmake;

./cmake/src/main;
./cmake/test/test;