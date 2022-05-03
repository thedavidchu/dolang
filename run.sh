#!/bin/bash

# This file is to test and run the 
cmake --build ./cmake;

./cmake/main >./test/output/stdout.log 2>./test/output/stderr.log;