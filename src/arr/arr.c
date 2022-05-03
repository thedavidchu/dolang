#include <assert.h>
#include <errno.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#include "mem/mem.h"

#include "arr/arr_checks.h"
#include "arr/arr_helper.h"
#include "arr/arr_macros.h"
#include "arr/arr.h"


/* 
NOTE: A possible addition is to store the `int (*item_dtor)(void *const)` in the
array. This way, we do not need to add it to the `arr_dtor`, `arr_change`, and
`arr_remove` calls. I advocate for doing this in an inheriting structure. */
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

int arr_dtor(arr *const me, int (*item_dtor)(void *const)) {
    int err = 0;
    size_t i = 0;

    if ((err = is_malformed(me))) {
        return -1;
    }
    /* Destroy each item. */
    for (i = 0; i < me->len; ++i) {
        /* We are not testing for error because I am not sure what to do if
        there is an error. I was thinking that we could move the error-producing
        item to the front and then reduce the array length to reflect the number
        of errors (i.e. we call `arr_remove` on the first pointer until
        we have gone through the whole list. This is slow, however. */
        item_dtor(ARR_GETITEM(me, i));
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

    /* Grow if necessary. */
    if (SHOULD_GROW(me)) {
        if ((err = arr_resize_nocheck(me, /*new_cap=*/GROWTH(me)))) {
            return err;
        }
    }

    /* Move to make space. */
    if ((err = arr_openhole_nocheck(me, idx))) {
        return err;
    }
    /* Increment length. */
    ++me->len;
    /* Copy in item. */
    if ((err = arr_copyitem_nocheck(me, idx, item))) {
        return err;
    }

    return 0;
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
    return ARR_GETITEM(me, idx);
}

int arr_change(const arr *const me, const size_t idx, void *const restrict item, int (*item_dtor)(void *const)) {
    int err = 0;
    
    if ((err = is_malformed(me)) || (err = is_outofbounds(me, idx))) {
        return err;
    }
    if ((err = arr_dtoritem_nocheck(me, idx, item_dtor))) {
        return err;
    }
    /* Copy in new item. */
    if ((err = arr_copyitem_nocheck(me, idx, item))) {
        return err;
    }
    return 0;
}

int arr_remove(arr *const me, const size_t idx, int (*item_dtor)(void *const)) {
    int err = 0;

    if ((err = is_malformed(me)) || (err = is_outofbounds(me, idx))) {
        return err;
    }
    if ((err = arr_dtoritem_nocheck(me, idx, item_dtor))) {
        return err;
    }
    if ((err = arr_closehole_nocheck(me, idx))) {
        return err;
    }

    /* Shrink the array if required. */
    if (SHOULD_SHRINK(me)) {
        if ((err = arr_resize_nocheck(me, /*new_cap=*/SHRINK(me)))) {
            return err;
        }
    }

    return 0;
}

int arr_stderr(const arr *const me, int (*item_stderr)(const void *const)) {
    int err = 0, tmperr = 0;
    size_t i = 0;

    if (0 > fprintf(stderr, "(len: %zu, cap: %zu, size: %zu) [", me->len, me->cap, me->size)) {
        assert(errno);
        return errno;
    }
    for (i = 0; i < me->len; ++i) {
        if ((tmperr = item_stderr(ARR_GETITEM(me, i)))) {
            err = tmperr;
            fprintf(stderr, "?");
        }
        fprintf(stderr, "%s", i == me->len - 1 ? "]" : ", ");
    }

    return err;
}
