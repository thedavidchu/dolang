#include <assert.h>
#include <string.h>

#include "src2/mem/mem.h"

#include "src2/arr/arr.h"

/* This block of code must not be imported to another translation unit, lest the
typedef be defined twice. */
#ifndef __STD_VERSION__
typedef unsigned char uint8_t;
#else
#   include <inttypes.h>
#endif

/** Check if the array is malformed. This means
    (1) $me == NULL,
    (2) $me->size = 0,
    (3) $me->cap > 0 but me->items == NULL, or
    (4) $me->cap < $me->len
*/
static inline int is_malformed(const arr *const me);
static inline int is_outofbounds(const arr *const me, const size_t idx);


static inline int is_malformed(const arr *const me) {
    if (me == NULL) {
        return -1;
    }
    /* We need to know that the size is not zero here, because for the next
    test, the number of bytes forming me->items is (me->cap * me->size), so we
    need to know that neither me->size nor me->cap are zero */
    if (me->size == 0) {
        return -1;
    }
    if (me->cap > 0 && me->items == NULL) {
        return -1;
    }
    if (me->cap < me->len) {
        return -1;
    }
    /* At this point, we know that 0 <= idx < len <= cap. This means that cap
    upper bounds all other values. We will check that me->cap * me->size does
    not overflow. */
    assert(0 <= me->len && me->len <= me->cap &&
           "unexpected mismatch in lenth or capacity!");
    
    /* We already know that me->size is not zero, but I am including it here
    for better documentation. */
    assert(me->size && "size is zero!");
    if (me->cap == (me->cap * me->size) / me->size) {
        return -1;
    }
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


int arr_ctor(arr *const me, const size_t cap, const size_t size) {
    int err = 0;

    /* The size has to be non-zero. Otherwise this is a very useless array. */
    if (size == 0) {
        return -1;
    }

    me->items = NULL;
    if ((err = mem_malloc((void **const)&me->items, cap, size))) {
        return err;
    }
    me->len = 0;
    me->cap = cap;
    me->size = size;
    return 0;
}

int arr_dtor(arr *const me) {
    int err = 0;

    if ((err = is_malformed(me))) {
        return -1;
    }
    me->len = 0;
    me->cap = 0;
    me->size = 0;
    /* Assumes the items pointer is a valid pointer */
    if ((err = mem_free((void **const)&me->items))) {
        return err;
    }
    assert(me->items == NULL && "$me->items not set to NULL!");
    return 0;
}

int arr_insert(arr *const me, const size_t idx, void *const item) {
    int err = 0;

    if ((err = is_malformed(me)) || (err = is_outofbounds(me, idx))) {
        return err;
    }
    assert(0 && "TODO(dchu)")
}

void *arr_search(const arr *const me, const size_t idx) {
    if (is_malformed(me) || is_outofbounds(me, idx)) {
        return NULL;
    }
    /* We assert me->size is not zero so we can do the division in the next
    statement. From the is_malformed() test, we know that neither of these
    can be true. */
    assert(me->size && "size is zero!");
    assert(idx == (idx * me->size) / me->size && "idx * me->size overflows!");
    return (void *)((uint8_t *)me->items)[idx * me->size];
}

int arr_change(const arr *const me, const size_t idx, void *const restrict item, int (*item_dtor)(void *)) {
    int err = 0;
    void *const dest = arr_search(me, idx);
    
    if ((err = is_malformed(me)) || (err = is_outofbounds(me, idx))) {
        return err;
    }
    if ((err = item_dtor(dest))) {
        return err;
    }
    memcpy(/*dest=*/dest, /*src=*/item, /*n=*/me->size);
    if (errno) {
        return errno;
    }
    return 0;
}

int arr_remove(arr *const me, const size_t idx, int (*item_dtor)(void *));
/* TODO(dchu) */