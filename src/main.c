#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

#include "bool/bool.h"
#include "mem/mem.h"

/* Print status and set test variable as pass or fail */
#define TEST_INT_EQ(output, oracle, err) \
do {\
    int _output = (output);\
    int _oracle = (oracle);\
    if (_output == _oracle) {\
        fprintf(stderr, #output " == " #oracle ": OK\n");\
    } else {\
        fprintf(stderr, /*RED*/"\033[31m" #output "(=%d) != " #oracle "(=%d)"\
            ", expected " #output " == " #oracle\
            ": FAILURE in %s:%d\033[0m\n"/*END RED*/,\
            _output, _oracle, __FILE__, __LINE__);\
        (err) = -1;\
    }\
} while (0)

/* Print status and set test variable as pass or fail */
#define TEST_PTR_EQ(output, oracle, err) \
do {\
    void *_output = (output);\
    void *_oracle = (oracle);\
    if (_output == _oracle) {\
        fprintf(stderr, #output " == " #oracle ": OK\n");\
    } else {\
        fprintf(stderr, /*RED*/"\033[31m" #output "(=%p) != " #oracle "(=%p)"\
            ", expected " #output " == " #oracle\
            ": FAILURE in %s:%d\033[0m\n"/*END RED*/,\
            _output, _oracle, __FILE__, __LINE__);\
        (err) = -1;\
    }\
} while (0)

/* Print status and set test variable as pass or fail */
#define TEST_PTR_NE(output, oracle, err) \
do {\
    void *_output = (output);\
    void *_oracle = (oracle);\
    if (_output != _oracle) {\
        fprintf(stderr, #output " != " #oracle ": OK\n");\
    } else {\
        fprintf(stderr, /*RED*/"\033[31m" #output "(=%p) == " #oracle "(=%p)"\
            ", expected " #output " != " #oracle\
            ": FAILURE in %s:%d\033[0m\n"/*END RED*/,\
            _output, _oracle, __FILE__, __LINE__);\
        (err) = -1;\
    }\
} while (0)

int test_bool(void) {
    /* Cannot use regular testing, because that relies upon the boolean working */
    assert((true && !false) && (true == 1 && false == 0));
    return 0;
}

int test_mem(void) {
    int err = 0;
    void *p = NULL, *tmp = NULL;

    /* Basic test malloc and free. */
    TEST_INT_EQ(mem_malloc(&p, 1, 1), 0, err);
    TEST_PTR_NE(p, NULL, err);
    TEST_INT_EQ(mem_free(&p), 0, err);
    TEST_PTR_EQ(p, NULL, err);

    /* Test bad arguments for mem_malloc() */
    TEST_INT_EQ(mem_malloc(NULL, 0, 1), -1, err);   /* Pass in NULL ptr => error*/
    TEST_INT_EQ(mem_malloc(NULL, 1, 1), -1, err);
    TEST_INT_EQ(mem_malloc(NULL, -1, 1), -1, err);
    TEST_INT_EQ(mem_malloc(&p, 0, 0), 0, err);
    TEST_PTR_EQ(p, NULL, err);   /* p returned as NULL */
    TEST_INT_EQ(mem_malloc(&p, -1, 1), ENOMEM, err);
    TEST_PTR_EQ(p, NULL, err); /* Not enough memory => error*/
    errno = 0;

    /* Test bad arguments for mem_free() */
    TEST_INT_EQ(mem_free(NULL), -1, err);

    /* Test bad arguments for  mem_realloc() */
    TEST_INT_EQ(mem_realloc(NULL, 0, 1), -1, err);   /* Pass in NULL ptr => error*/
    TEST_INT_EQ(mem_realloc(NULL, 1, 1), -1, err);
    TEST_INT_EQ(mem_realloc(NULL, -1, 1), -1, err);
    TEST_INT_EQ(mem_realloc(&p, 0, 1), 0, err);
    TEST_PTR_EQ(p, NULL, err);
    TEST_INT_EQ(mem_realloc(&p, -1, 1), ENOMEM, err);
    TEST_PTR_EQ(p, NULL, err);
    /* errno still set! */
    TEST_INT_EQ(mem_realloc(NULL, 0, 1),  ENOMEM, err);   /* Pass in NULL ptr => error*/
    TEST_INT_EQ(mem_realloc(NULL, 1, 1),  ENOMEM, err);
    TEST_INT_EQ(mem_realloc(NULL, -1, 1), ENOMEM, err);
    TEST_INT_EQ(mem_realloc(&p, 0, 1),    ENOMEM, err);   /* Pass in ptr => error*/
    TEST_INT_EQ(mem_realloc(&p, 1, 1),    ENOMEM, err);
    TEST_INT_EQ(mem_realloc(&p, -1, 1),   ENOMEM, err);
    errno = 0;

    TEST_INT_EQ(mem_realloc(&p, 10, 1), 0, err);
    TEST_PTR_NE(p, NULL, err); /* Works */
    TEST_INT_EQ(mem_realloc(&p, 0, 1), 0, err);
    TEST_PTR_EQ(p, NULL, err);
    TEST_INT_EQ(mem_realloc(&p, 10, 1), 0, err);
    TEST_PTR_NE(p, NULL, err);
    tmp = p;
    TEST_INT_EQ(mem_realloc(&p, -1, 1), ENOMEM, err);
    TEST_PTR_NE(p, NULL, err);
    TEST_PTR_EQ(p, tmp, err);
    errno = 0;
    tmp = NULL;
    TEST_INT_EQ(mem_realloc(&p, 0, 1), 0, err);
    TEST_PTR_EQ(p, NULL, err);

    return err;
}

int test_arr(void) {
    int err = 0;

    return err;

}

int main(void) {
    int err = 0;
    
    /* Technically, this is sketchy because we are assuming that bool works. */
    TEST_INT_EQ(test_bool(), 0, err);
    TEST_INT_EQ(test_mem(), 0, err);

    return err;
}