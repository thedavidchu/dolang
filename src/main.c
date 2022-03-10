#include <assert.h>
#include <stdio.h>

#include "bool/bool.h"
#include "mem/mem.h"

/* Print status and set test variable as pass or fail */
#define TEST(expression, test_var) \
do {\
    if (expression) {\
        fprintf(stderr, #expression ": OK\n");\
    } else {\
        fprintf(stderr, /*RED*/"\033[31m" #expression ": FAILURE\033[0m\n"/*END RED*/);\
        test_var = false;\
    }\
} while (0)

int test_bool(void) {
    /* Cannot use regular testing, because that relies upon the boolean working */
    assert((true && !false) && (true == 1 && false == 0));
    return 1;
}

bool test_mem(void) {
    bool pass = true;
    void *p;
    TEST(!mem_new(&p, 10), pass);
    TEST(p, pass);
    TEST(!mem_del(&p), pass);
    TEST(!p, pass);
    return pass;
}

int main(void) {
    bool pass = true;
    
    /* Technically, this is sketchy because we are assuming that bool works. */
    TEST(test_bool(), pass);
    TEST(test_mem(), pass);

    return (int)pass;
}