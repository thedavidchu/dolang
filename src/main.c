#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

#include "common/common.h"
#include "bool/bool.h"
#include "mem/mem.h"
#include "arr/arr.h"
#include "tbl/tbl.h"
#include "rstr/rstr.h"

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
        fprintf(CHANNEL, /*GREEN*/"\033[32m" #output " == " #oracle ": OK\033[0m\n"/*END GREEN*/);\
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
        fprintf(CHANNEL, /*GREEN*/"\033[32m" #output " != " #oracle ": OK\033[0m\n"/*END GREEN*/);\
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
    assert(str != NULL && "null str");
    printf("\"%s\"", (const char *const restrict)str);
    return 0;
}

int tbl_noop_del(void *const restrict ptr) {
    assert(ptr != NULL && "pointer is NULL");
    return 0;
}

int test_tbl(void) {
    int err = 0;
    size_t i = 0;
    char *keys[10] = {
        "a", "bb", "ccc", "dddd", "eeeee", "ffffff", "ggggggg", "hhhhhhhh",
        "iiiiiiiii", "jjjjjjjjjj"
    };
    int values[10] = {10, 11, 12, 13, 14, 15, 16, 17, 18, 19};
    tbl *me = NULL;

    /* Setup */
    REQUIRE_NO_ERROR(mem_malloc((void **)&me, 1, sizeof(tbl)),
            "malloc failed");
    REQUIRE_NO_ERROR(tbl_ctor(me, 10, simple_str_hash,
            (int (*)(const void *const restrict, const void *const restrict))strcmp),
            "tbl_ctor failed");
    
    TEST_INT_EQ(tbl_print(me, str_print, int_print), 0, err);
    TEST_INT_EQ(tbl_insert(me, keys[0], &values[0], tbl_noop_del), 0, err);
    TEST_INT_EQ(tbl_insert(me, keys[1], &values[1], tbl_noop_del), 0, err);
    TEST_INT_EQ(tbl_print(me, str_print, int_print), 0, err);

    TEST_PTR_EQ(tbl_search(me, keys[0]), &values[0], err);
    TEST_PTR_EQ(tbl_search(me, keys[1]), &values[1], err);
    TEST_PTR_EQ(tbl_search(me, keys[2]), NULL, err);

    TEST_INT_EQ(tbl_remove(me, keys[0], tbl_noop_del, tbl_noop_del), 0, err);
    TEST_INT_EQ(tbl_remove(me, keys[0], tbl_noop_del, tbl_noop_del), 0, err);
    TEST_PTR_EQ(tbl_search(me, keys[0]), NULL, err);
    TEST_INT_EQ(tbl_print(me, str_print, int_print), 0, err);

    TEST_INT_EQ(tbl_insert(me, keys[0], &values[0], tbl_noop_del), 0, err);
    TEST_PTR_EQ(tbl_search(me, keys[0]), &values[0], err);
    TEST_INT_EQ(tbl_print(me, str_print, int_print), 0, err);

    TEST_INT_EQ(tbl_insert(me, keys[0], &values[1], tbl_noop_del), 0, err);
    TEST_INT_EQ(tbl_print(me, str_print, int_print), 0, err);
    TEST_PTR_EQ(tbl_search(me, keys[0]), &values[1], err);
    TEST_INT_EQ(tbl_insert(me, keys[0], &values[0], tbl_noop_del), 0, err);
    TEST_INT_EQ(tbl_print(me, str_print, int_print), 0, err);

    for (i = 0; i < 10; ++i) {
        TEST_INT_EQ(tbl_insert(me, keys[i], &values[i], tbl_noop_del), 0, err);
        TEST_INT_EQ(tbl_print(me, str_print, int_print), 0, err);
        TEST_PTR_EQ(tbl_search(me, keys[i]), &values[i], err);
    }
    /* Try to shove an extra in (breaks for now) */
    TEST_INT_EQ(tbl_insert(me, "extra", &values[0], tbl_noop_del), ERROR_NOROOM, err);

    for (i = 0; i < 10; ++i) {
        TEST_INT_EQ(tbl_remove(me, keys[i], tbl_noop_del, tbl_noop_del), 0, err);
    }
    TEST_INT_EQ(tbl_remove(me, keys[0], tbl_noop_del, tbl_noop_del), 0, err);

    TEST_INT_EQ(tbl_print(me, str_print, int_print), 0, err);
    for (i = 0; i < 10; ++i) {
        TEST_INT_EQ(tbl_insert(me, keys[i], &values[i], tbl_noop_del), 0, err);
        TEST_INT_EQ(tbl_print(me, str_print, int_print), 0, err);
        TEST_PTR_EQ(tbl_search(me, keys[i]), &values[i], err);
    }
    TEST_INT_EQ(tbl_print(me, str_print, int_print), 0, err);

    /* Teardown */
    REQUIRE_NO_ERROR(tbl_dtor(me, tbl_noop_del, tbl_noop_del),
            "tbl_dtor failed");
    REQUIRE_NO_ERROR(mem_free((void **)&me), "free failed");

    return err;
}

/******************************************************************************/
int rstr_noop_dtor(char *const str) {
    assert(str && "found NULL string");
    return 0;
}

int test_rstr(void) {
    int err = 0;
    rstr full, a, b;
    const char *const str = "Lorem ipsum dolor sit amet, consectetur adipiscing elit";

    REQUIRE_NO_ERROR(rstr_ctor(&full, str, strlen(str)), "failure to construct");
    REQUIRE_NO_ERROR(rstr_debug(&full), "failure to print");
    REQUIRE_NO_ERROR(rstr_print(&full), "failure to print");

    TEST_INT_EQ(rstr_debug(NULL), ERROR_NULLPTR, err);
    a.str = NULL;
    TEST_INT_EQ(rstr_debug(&a), ERROR_NULLPTR, err);

    TEST_INT_EQ(rstr_ctor(&a, str, 10U), 0, err);
    TEST_INT_EQ(a.len, 10U, err);
    TEST_INT_EQ(rstr_debug(&a), 0, err);

    TEST_INT_EQ(rstr_slice(&full, 0, 10, &b), 0, err);
    TEST_INT_EQ(rstr_debug(&b), 0, err);

    TEST_INT_EQ(rstr_cmp(&a, &b), 0, err);

    TEST_INT_EQ(rstr_slice(&b, 0, 5, &b), 0, err);
    TEST_INT_EQ(rstr_debug(&b), 0, err);


    /* Cleanup */
    TEST_INT_EQ(rstr_dtor(&full, rstr_noop_dtor), 0, err);
    TEST_INT_EQ(rstr_dtor(&a, rstr_noop_dtor), 0, err);
    TEST_INT_EQ(rstr_dtor(&b, rstr_noop_dtor), 0, err);

    return err;
}

int main(void) {
    int err = 0;

    /* Technically, this is sketchy because we are assuming that bool works. */
    TEST_INT_EQ(test_bool(), 0, err);
    TEST_INT_EQ(test_mem(), 0, err);
    TEST_INT_EQ(test_arr(), 0, err);
    TEST_INT_EQ(test_tbl(), 0, err);
    TEST_INT_EQ(test_rstr(), 0, err);

    if (err == 0) {
        fprintf(CHANNEL, /*GREEN*/"\033[32m>>> ALL TESTS PASSED! <<<\033[0m\n"/*END GREEN*/);
        fflush(CHANNEL);
    }

    return err;
}
