#pragma once

#include <assert.h>
#include <stddef.h>

#include "mem/mem.h"

#include "arr/arr_checks.h"
#include "arr/arr_macros.h"
#include "arr/arr.h"    /* arr */

static inline int arr_dtoritem_nocheck(const arr *const me, const size_t idx, int (*item_dtor)(void *const));
static inline int arr_resize_nocheck(arr *const me, const size_t new_cap);
static inline int arr_copyitem_nocheck(const arr *const me, const size_t src_idx, void *const restrict item);

static inline int arr_openhole_nocheck(arr *const me, const size_t hole_idx);
static inline int arr_closehole_nocheck(arr *const me, const size_t hole_idx);

static inline int arr_dtoritem_nocheck(const arr *const me, const size_t idx, int (*item_dtor)(void *const)) {
    int err = 0;
    void *const arr_item = ARR_GETITEM(me, idx);

    if ((err = item_dtor(arr_item))) {
        return err;
    }
    return 0;
}

static inline int arr_resize_nocheck(arr *const me, const size_t new_cap) {
    int err = 0;

    /* Resize */
    if ((err = mem_realloc((void **const)&me->items, new_cap, me->size))) {
        return err;
    }
    me->cap = new_cap;
    return 0;
}

static inline int arr_copyitem_nocheck(const arr *const me, const size_t idx, void *const item) {
    int err = 0;

    if ((err = mem_memcpy(/*src=*/item, /*dst=*/ARR_GETITEM(me, idx), /*num=*/1, /*size=*/me->size))) {
        return err;
    }
    return 0;
}

static inline int arr_openhole_nocheck(arr *const me, const size_t hole_idx) {
    int err = 0;

    assert(me->cap >= me->len + 1 && "not enough room to expand!");
    assert(hole_idx <= me->len &&
        "is this assertion necessary? checks for valid hole_idx");
    /*
    len = 4
     0-1-2-3-  4-5-6-
    [ A B C D | X X X ]*/
    if (hole_idx < me->len) {
        void *const src = ARR_GETITEM(me, hole_idx);
        void *const dst = ARR_GETITEM(me, hole_idx + 1);

        if ((err = mem_memmove(src, dst, me->len - hole_idx, me->size))) {
            return err;
        }
    }
    me->len += 1;
    return 0;
}

static inline int arr_closehole_nocheck(arr *const me, const size_t hole_idx) {
    int err = 0;
    
    assert(hole_idx <= me->len && "hole index is too large.");
    if (hole_idx < me->len - 1) { /* Not the last valid idx. [X X X] */
        /* We declare this in a new block because we need to declare these after
        the first error check. */
        void *const src = ARR_GETITEM(me, hole_idx + 1);
        void *const dst = ARR_GETITEM(me, hole_idx);

        if ((err = mem_memmove(src, dst, me->len - hole_idx - 1, me->size))) {
            return err;
        }
    }
    me->len -= 1;
    return 0;
}
