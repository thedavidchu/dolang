#include "unity.h"

void setUp(void) {
    // set stuff up here
}

void tearDown(void) {
    // clean stuff up here
}

void my_test(void) {}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(my_test);
    return UNITY_END();
}