#pragma once

#include <assert.h>
#include <stddef.h>

#include "arr/arr.h" /* arr */

/** Check if the array is malformed. This means
    (1) $me == NULL,
    (2) $me->size = 0,
    (3) $me->cap > 0 but me->items == NULL, or
    (4) $me->cap < $me->len
*/
static inline int is_malformed(const arr *const me);

/** Check if the index is out of bounds. It is important to call `is_malformed`
before this function, because we make assertions in this functions that are
checked by tests in the `is_malformed` function. (i.e. the program will error
out instead of returning an appropriate error value).

Note that the index 0 is out of bounds for an array of length 0. */
static inline int is_outofbounds(const arr *const me, const size_t idx);
static inline int is_outofinsertbounds(const arr *const me, const size_t idx);

static inline int is_malformed(const arr *const me) {
    RETURN_IF_ERROR(me == NULL, -1);
    /* We need to know that the size is not zero here, because for the next
    test, the number of bytes forming me->items is (me->cap * me->size), so we
    need to know that neither me->size nor me->cap are zero */
    RETURN_IF_ERROR(me->size == 0, -1);
    RETURN_IF_ERROR(me->cap > 0 && me->items == NULL, -1);
    RETURN_IF_ERROR(me->cap < me->len, -1);
    /* At this point, we know that 0 <= idx < len <= cap. This means that cap
    upper bounds all other values. We will check that me->cap * me->size does
    not overflow. */
    assert(/* 0 <= me->len (always true bc unsigned) */ me->len <= me->cap &&
           "unexpected mismatch in lenth or capacity!");

    /* We already know that me->size is not zero, but I am including it here
    for better documentation. */
    assert(me->size && "size is zero!");
    RETURN_IF_ERROR(me->cap != (me->cap * me->size) / me->size, -1);
    return 0;
}

static inline int is_outofbounds(const arr *const me, const size_t idx) {
    /* We assert me->size is not zero so we can do the division in the next
    statement. From the is_malformed() test, we know that neither of these
    can be true. */
    assert(me->size && "size is zero!");
    assert(idx == (idx * me->size) / me->size && "idx * me->size overflows!");
    if (idx >= me->len) {
        return -1;
    }
    return 0;
}

static inline int is_outofinsertbounds(const arr *const me, const size_t idx) {
    /* We assert me->size is not zero so we can do the division in the next
    statement. From the is_malformed() test, we know that neither of these
    can be true. */
    assert(me->size && "size is zero!");
    assert(idx == (idx * me->size) / me->size && "idx * me->size overflows!");
    if (idx > me->len) {
        return -1;
    }
    return 0;
}
