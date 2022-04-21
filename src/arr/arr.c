#include <assert.h>
#include <errno.h>
#include <string.h>

#include "src2/mem/mem.h"

#include "src2/arr/arr.h"

/* This block of code must not be imported to another translation unit, lest the
typedef be defined twice. */
#ifndef __STD_VERSION__
typedef unsigned char Byte;
#else
#   include <inttypes.h>
typedef uint8_t Byte;
#endif

/* Assuming that $idx * $size is a valid multiplication and that the offset
generated will create a valid address from $ptr. */
#define ARR_GETITEM(me, idx) (void *)&((Byte *)(me)->items)[(idx) * ((me)->size)]

#define SHOULD_GROW(me) ((me)->cap == (me)->len)
#define GROWTH(me) (((me)->cap > 4) ? (me)->cap * 2 : 4)
#define SHOULD_SHRINK(me) ((me)->cap / 4 >= (me)->len)
#define SHRINK(me) (((me)->cap > 4) ? (me)->cap / 2 : 4)

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
static inline int arr_resize(arr *const me, const size_t new_cap);
static inline int arr_cpitem(arr *const me, const size_t idx, void *const item);


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

static inline int arr_resize(arr *const me, const size_t new_cap) {
    int err = 0;

    /* Error checking. */
    if ((err = is_malformed(me))) {
        return err;
    }
    /* Resize */
    if ((err = mem_realloc((void **const)&me->items, new_cap, me->size))) {
        return err;
    }
    me->cap = new_cap;
    return 0;
}

static inline int arr_cpitem(arr *const me, const size_t idx, void *const item) {
    int err = 0;
    void const *ret = 0;

    if ((err = is_malformed(me)) || (err = is_outofbounds(me, idx))) {
        return err;
    }
    if (errno) {
        return errno;
    }
    if ((ret = memcpy(/*dst=*/ARR_GETITEM(me, idx), /*src=*/item,
                      /*n=*/me->size)) == NULL ||
            errno) {
            assert(ret == NULL && errno &&
                "error return and error code are mismatched!");
            return errno;
        }
    }
    assert(ret != NULL && errno == 0 &&
        "no error returned but error code claims error!");
        return 0;
}

static inline int arr_shift(arr *const me, const size_t src_idx, const size_t dst_idx) {
    if ((err = is_malformed(me)) || (err = is_outofbounds(me, src_idx))) {
        return err;
    }
    if (errno) {
        return errno;
    }

    assert(0 && "TODO(dchu)!");
}


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
    void const *res = NULL;

    if ((err = is_malformed(me)) || (err = is_outofbounds(me, idx))) {
        return err;
    }

    /* Grow if necessary. */
    if (SHOULD_GROW(me)) {
        if ((err = arr_resize(me, /*new_cap=*/GROWTH(me)))) {
            return err;
        }
    }

    /* Move to make space. */
    arr_shift(...); /* TODO(dchu)
    /* Increment length. */
    ++me->len;
    /* Copy in item. */
    if ((err = arr_cpitem(me, idx, item))) {
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

int arr_change(const arr *const me, const size_t idx, void *const restrict item, int (*item_dtor)(void *)) {
    int err = 0;
    void const *ret = NULL;
    
    /* Error checking. */
    if ((err = is_malformed(me)) || (err = is_outofbounds(me, idx))) {
        return err;
    }
    /* Remove old item. */
    if ((err = item_dtor(dst))) {
        return err;
    }
    /* Copy in new item. */
    if ((err = arr_cpitem(me, idx, item))) {
        return err;
    }
    return 0;
}

int arr_remove(arr *const me, const size_t idx, int (*item_dtor)(void *const)) {
    int err = 0;
    void const *ret = NULL;

    /* Error checking. */
    if ((err = is_malformed(me)) || (err = is_outofbounds(me, idx))) {
        return err;
    }

    /* Delete item. */
    if ((err = item_dtor(dst))) {
        return err;
    }

    /* We must check the errno in case item_dtor sets it. We cannot guarantee
    that it sets/tests the errno, so we cannot throw an assertion. */
    if (errno) { return errno; }
    /* I am assuming that `memmove` returns the pointer to the `dst`. */
    if (me->len > 1 && 
        (ret = memmove(/*dst=*/ARR_GETITEM(me, idx), /*src=*/ARR_GETITEM(me, idx + 1),
                       /*n=*/(me->len - (idx + 1)) * me->size)) == NULL ||
        errno) {
        assert(ret == NULL && errno &&
            "error return and error code are mis-matched!");
        return errno;
    }
    assert(ret != NULL && errno == 0 &&
        "no error returned but error code claims error!");
    --me->len;

    /* Shrink the array if required. */
    if (SHOULD_SHRINK(me)) {
        if ((err = arr_resize(me, /*new_cap=*/SHRINK(me)))) {
            return err;
        }
    }

    return 0;
}