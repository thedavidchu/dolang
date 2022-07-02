#include <assert.h>
#include <errno.h>
#include <stdlib.h>

#include "unity.h"

#include "src/mem/mem.h"
#include "src/mem/mem_overflow.h"

#define RESET_FREE(ptr)                                                        \
    do {                                                                       \
        errno = 0;                                                             \
        free(ptr);                                                             \
        ptr = NULL;                                                            \
    } while (0)

#define RESET_MALLOC(ptr)                                                      \
    do {                                                                       \
        errno = 0;                                                             \
        assert(ptr == NULL && "non-null ptr");                                 \
        ptr = malloc(1);                                                       \
        assert(ptr != NULL && "failed to alloc");                              \
    } while (0)

int valid_ptr[1] = {0};

void setUp(void) {
    // set stuff up here
}

void tearDown(void) {
    // clean stuff up here
}

void test_is_overflow(void) {
    /* Any zeros */
    TEST_ASSERT_EQUAL_INT(0, is_overflow(0, 0));
    TEST_ASSERT_EQUAL_INT(0, is_overflow(0, -1));
    TEST_ASSERT_EQUAL_INT(0, is_overflow(-1, 0));

    /* Valid */
    TEST_ASSERT_EQUAL_INT(0, is_overflow(1, 1));
    TEST_ASSERT_EQUAL_INT(0, is_overflow(1, -1));
    TEST_ASSERT_EQUAL_INT(0, is_overflow(-1, 1));

    /* Invalid */
    TEST_ASSERT_EQUAL_INT(-1, is_overflow(2, -1));
    TEST_ASSERT_EQUAL_INT(-1, is_overflow(-1, 2));
    TEST_ASSERT_EQUAL_INT(-1, is_overflow(-1, -1));
}

void test_mem_malloc(void) {
    void *p = NULL;

    /* Errno carry over */
    errno = ENOMEM;
    TEST_ASSERT_EQUAL_INT(ENOMEM, mem_malloc(&p, 1, 1));
    TEST_ASSERT_EQUAL_INT(ENOMEM, errno);
    TEST_ASSERT_NULL(p);

    RESET_FREE(p);

    /* Overflow */
    TEST_ASSERT_EQUAL_INT(-1, mem_malloc(&p, -1, -1));
    TEST_ASSERT_EQUAL_INT(0, errno);
    TEST_ASSERT_NULL(p);

    RESET_FREE(p);

    /* Pass NULL */
    TEST_ASSERT_EQUAL_INT(-1, mem_malloc(NULL, 1, 1));
    TEST_ASSERT_EQUAL_INT(0, errno);
    TEST_ASSERT_NULL(p);

    RESET_FREE(p);

    /* Pass non-NULL Pointer */
    p = (void *)valid_ptr;
    TEST_ASSERT_EQUAL_INT(-1, mem_malloc(&p, 1, 1));
    TEST_ASSERT_EQUAL_INT(0, errno);
    TEST_ASSERT(p == (void *)valid_ptr);

    p = NULL; /* we need to manually reset it here so we don't try freeing the
  valid pointer. */
    RESET_FREE(p);

    /* Return NULL when zero size */
    TEST_ASSERT_EQUAL_INT(0, mem_malloc(&p, 0, 0));
    TEST_ASSERT_EQUAL_INT(0, errno);
    TEST_ASSERT_NULL(p);

    RESET_FREE(p);

    /* Test invalid size */
    TEST_ASSERT_EQUAL_INT(ENOMEM, mem_malloc(&p, 1, -1));
    TEST_ASSERT_EQUAL_INT(ENOMEM, errno);
    TEST_ASSERT_NULL(p);

    RESET_FREE(p);

    /* Test valid size */
    TEST_ASSERT_EQUAL_INT(0, mem_malloc(&p, 1, 1));
    TEST_ASSERT_EQUAL_INT(0, errno);
    TEST_ASSERT_NOT_NULL(p);

    RESET_FREE(p); /* final free */
}

void test_mem_realloc(void) {
    void *p = NULL;
    void *old_ptr = NULL;

    /* Errno carry over */
    errno = ENOMEM;
    TEST_ASSERT_EQUAL_INT(ENOMEM, mem_realloc(&p, 1, 1));
    TEST_ASSERT_EQUAL_INT(ENOMEM, errno);
    TEST_ASSERT_NULL(p);

    RESET_FREE(p);

    /* Overflow */
    TEST_ASSERT_EQUAL_INT(-1, mem_realloc(&p, -1, -1));
    TEST_ASSERT_EQUAL_INT(0, errno);
    TEST_ASSERT_NULL(p);

    RESET_FREE(p);

    /* Pass NULL */
    TEST_ASSERT_EQUAL_INT(-1, mem_realloc(NULL, 1, 1));
    TEST_ASSERT_EQUAL_INT(0, errno);
    TEST_ASSERT_NULL(p);

    RESET_FREE(p);

    /* Zero size */
    TEST_ASSERT_EQUAL_INT(0, mem_realloc(&p, 0, 0));
    TEST_ASSERT_EQUAL_INT(0, errno);
    TEST_ASSERT_NULL(p);

    RESET_FREE(p);
    RESET_MALLOC(p);

    /* Zero size but valid pointer */
    assert(p && "no alloc");
    TEST_ASSERT_EQUAL_INT(0, mem_realloc(&p, 0, 0));
    TEST_ASSERT_EQUAL_INT(0, errno);
    TEST_ASSERT_NULL(p);

    RESET_FREE(p);
    RESET_MALLOC(p);

    /* Invalid (not null) */
    old_ptr = p;
    assert(p && old_ptr && "no alloc");
    TEST_ASSERT_EQUAL_INT(ENOMEM, mem_realloc(&p, 1, -1));
    TEST_ASSERT_EQUAL_INT(ENOMEM, errno);
    TEST_ASSERT_NOT_NULL(p);
    TEST_ASSERT_EQUAL_PTR(old_ptr, p);

    RESET_FREE(p);
    RESET_MALLOC(p);

    /* Valid */
    assert(p && "no alloc");
    old_ptr = p;
    TEST_ASSERT_EQUAL_INT(0, mem_realloc(&p, 1, 1));
    TEST_ASSERT_EQUAL_INT(0, errno);

    RESET_FREE(p);
    old_ptr = NULL; /* only 1 free per pointer */
}

void test_mem_free(void) {
    void *p = NULL;

    /* Initial malloc */
    RESET_MALLOC(p);

    /* errno already set */
    errno = ENOMEM;
    TEST_ASSERT_EQUAL_INT(ENOMEM, mem_free(&p));
    TEST_ASSERT_EQUAL_INT(ENOMEM, errno);
    TEST_ASSERT_NOT_NULL(p);

    RESET_FREE(p);   /* free p */
    RESET_MALLOC(p); /* alloc p */

    /* Pass NULL */
    TEST_ASSERT_EQUAL_INT(-1, mem_free(NULL));
    TEST_ASSERT_EQUAL_INT(0, errno);
    TEST_ASSERT_NOT_NULL(p);

    RESET_FREE(p);   /* free p */
    RESET_MALLOC(p); /* alloc p */

    /* Valid (p != NULL)*/
    TEST_ASSERT_EQUAL_INT(0, mem_free(&p));
    TEST_ASSERT_EQUAL_INT(0, errno);
    TEST_ASSERT_NULL(p);

    /* Valid (p == NULL)*/
    TEST_ASSERT_EQUAL_INT(0, mem_free(&p));
    TEST_ASSERT_EQUAL_INT(0, errno);
    TEST_ASSERT_NULL(p);

    /* no malloc at the end */
}

int main(void) {
    UNITY_BEGIN();

    RUN_TEST(test_is_overflow);
    RUN_TEST(test_mem_malloc);
    RUN_TEST(test_mem_realloc);
    RUN_TEST(test_mem_free);

    return UNITY_END();
}
