#include "unity.h"

#include "test/test_bool.h"

void setUp(void) {
    // set stuff up here
}

void tearDown(void) {
    // clean stuff up here
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_bool);
    return UNITY_END();
}