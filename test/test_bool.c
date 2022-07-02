#include "unity.h"

#include "src/bool/bool.h"

void setUp(void) {
    // set stuff up here
}

void tearDown(void) {
    // clean stuff up here
}

void test_bool(void) {
    TEST_ASSERT(true == 1);
    TEST_ASSERT(false == 0);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_bool);
    return UNITY_END();
}

