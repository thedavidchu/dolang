#include <assert.h>
#include <errno.h>
#include <stdio.h>

#include "bool/bool.h"
#include "mem/mem.h"

/* Print status and set test variable as pass or fail */
#define TEST(expression, test_var) \
do {\
    if ((expression)) {\
        fprintf(stderr, #expression ": OK\n");\
    } else {\
        fprintf(stderr,\
            /*RED*/"\033[31m" #expression\
            ": FAILURE in %s:%d\033[0m\n"/*END RED*/,\
            __FILE__, __LINE__);\
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
    void *p, *tmp;

    /* Basic test malloc and free. */
    TEST(!mem_new(&p, 1) && p != NULL, pass);
    TEST(!mem_del(&p) && p == NULL, pass);

    /* Test bad arguments for mem_new() */
    TEST(mem_new(NULL, 0), pass);   /* Pass in NULL ptr => error*/
    TEST(mem_new(NULL, 1), pass);
    TEST(mem_new(NULL, -1), pass);
    TEST(!mem_new(&p, 0) && p == NULL, pass);   /* p returned as NULL */
    TEST(ENOMEM == mem_new(&p, -1) && p == NULL, pass); /* Not enough memory => error*/
    errno = 0;

    /* Test bad arguments for mem_del() */
    TEST(mem_del(NULL), pass);

    /* Test bad arguments for mem_resize() */
    TEST(mem_resize(NULL, 0), pass);   /* Pass in NULL ptr => error*/
    TEST(mem_resize(NULL, 1), pass);
    TEST(mem_resize(NULL, -1), pass);
    TEST(!mem_resize(&p, 0) && p == NULL, pass);
    TEST(ENOMEM == mem_resize(&p, -1) && p == NULL, pass);
    errno = 0;

    TEST(!mem_resize(&p, 10) && p != NULL, pass); /* Works */
    TEST(!mem_resize(&p, 0) && p == NULL, pass);
    TEST(!mem_resize(&p, 10) && p != NULL, pass);
    tmp = p;
    TEST(ENOMEM == mem_resize(&p, -1) && p != NULL && p == tmp, pass);
    errno = 0;
    tmp = NULL;
    TEST(!mem_resize(&p, 0) && p == NULL, pass);


    return pass;
}

int main(void) {
    bool pass = true;
    
    /* Technically, this is sketchy because we are assuming that bool works. */
    TEST(test_bool(), pass);
    TEST(test_mem(), pass);

    return (int)pass;
}