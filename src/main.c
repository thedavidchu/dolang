#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

#include "bool/bool.h"
#include "mem/mem.h"
#include "arr/arr.h"
#include "tbl/tbl.h"

#define CHANNEL stdout

/* Print status and set test variable as pass or fail */
#define TEST_INT_EQ(output, oracle, err) \
do {\
    int _output = (output);\
    int _oracle = (oracle);\
    if (_output == _oracle) {\
        fprintf(CHANNEL, /*GREEN*/"\033[32m" #output " == " #oracle ": OK\033[0m\n"/*END GREEN*/);\
    } else {\
        fprintf(CHANNEL, /*RED*/"\033[31m" #output "(=%d) != " #oracle "(=%d)"\
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
        fprintf(CHANNEL, #output " == " #oracle ": OK\n");\
    } else {\
        fprintf(CHANNEL, /*RED*/"\033[31m" #output "(=%p) != " #oracle "(=%p)"\
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
        fprintf(CHANNEL, #output " != " #oracle ": OK\n");\
    } else {\
        fprintf(CHANNEL, /*RED*/"\033[31m" #output "(=%p) == " #oracle "(=%p)"\
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

/******************************************************************************/

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

/******************************************************************************/

int int_print(const void *const restrict ip) {
    printf("%d", *(int *)ip);
    return 0;
}

int int_dtor(void *const restrict ip) {
    if (ip == NULL) {
        return -1;
    }
    return 0;
}

int test_arr(void) {
    int err = 0, x = 0;
    int *y = NULL;
    arr a = { 0 }, b = { 0 };

    TEST_INT_EQ(arr_ctor(&a, 10, sizeof(int)), 0, err);
    TEST_INT_EQ(arr_ctor(&b, 10, sizeof(int)), 0, err);

    arr_print(&a, int_print);
    for (x = 0; x < 11; ++x) {
        TEST_INT_EQ(arr_insert(&a, 0, &x), 0, err);
        y = (int *)arr_search(&a, 0);
        assert(y != NULL && "null!");
        TEST_INT_EQ(*y == x, 1, err);
    }
    arr_print(&a, int_print);

    for (x = 11; x < 22; ++x) {
        TEST_INT_EQ(arr_append(&a, &x), 0, err);
    }
    arr_print(&a, int_print);

    x = 12;
    TEST_INT_EQ(arr_change(&a, 0, &x, int_dtor), 0, err);
    arr_print(&a, int_print);

    while (a.len > 0) {
        TEST_INT_EQ(arr_remove(&a, 0, int_dtor), 0, err);
    }
    arr_print(&a, int_print);

    TEST_INT_EQ(arr_dtor(&a, int_dtor), 0, err);
    TEST_INT_EQ(arr_dtor(&b, int_dtor), 0, err);

    return err;
}

/******************************************************************************/

size_t simple_str_hash(const void *const restrict str) {
    return strlen((const char *const restrict)str);
}

int str_print(const void *const restrict str) {
    assert(str && "null str");
    fputs((const char *const restrict)str, stdout);
    return 0;
}

int tbl_noop_del(void *const restrict ptr) {
    assert(ptr && "pointer is NULL");
    return 0;
}

int test_tbl(void) {
    int err = 0;
    tbl *me = NULL;

    assert(mem_malloc((void **)&me, 1, sizeof(tbl)) == 0);
    assert(tbl_ctor(me, 10, simple_str_hash,
            (int (*)(const void *const restrict, const void *const restrict))strcmp) == 0);
    tbl_print(me, str_print, int_print);
    tbl_insert(me, "hello", &err, tbl_noop_del);
    tbl_insert(me, "hello2", &err, tbl_noop_del);
    tbl_print(me, str_print, int_print);
    TEST_PTR_EQ(tbl_search(me, "hello"), &err, err);
    TEST_PTR_EQ(tbl_search(me, "hello2"), &err, err);
    TEST_PTR_EQ(tbl_search(me, "hello3"), NULL, err);
    tbl_remove(me, "hello", tbl_noop_del, tbl_noop_del);
    TEST_PTR_EQ(tbl_search(me, "hello"), NULL, err);
    
    assert(tbl_dtor(me, tbl_noop_del, tbl_noop_del) == 0);
    assert(mem_free((void **)&me) == 0);

    return err;
}

int main(void) {
    int err = 0;
    
    /* Technically, this is sketchy because we are assuming that bool works. */
    TEST_INT_EQ(test_bool(), 0, err);
    TEST_INT_EQ(test_mem(), 0, err);
    TEST_INT_EQ(test_arr(), 0, err);
    TEST_INT_EQ(test_tbl(), 0, err);

    return err;
}
