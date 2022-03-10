#include <assert.h>
#include <stdlib.h>
#include <errno.h>

#include "mem.h"

int mem_new(void **const p, const size_t size) {
    /* Check for unhandled errors. */
    if (errno) {
        assert(!errno && "unhandled error before malloc.");
        return errno;
    }

    if (!size) {
        *p = NULL;
        return 0;
    }
    /* We do not check if there is already a value, so this may overwrite values */
    if (!(*p = malloc(size))) {
        /* *p is NULL becasue of malloc. Check that errno != 0; if errno = 0,
        then something fishy is going on, so return -1. */
        return errno ? errno : -1;
    }
    /* *p is a valid pointer => errno = 0 */
    return 0;
}

int mem_del(void **const p) {
    /* Check for unhandled errors. */
    if (errno) {
        assert(!errno && "unhandled error before free.");
        return errno;
    }

    if (*p) {
        free(*p);
        if (!errno) {
            *p = NULL;
        }
    }
    return errno;
}

int mem_resize(void **const p, const size_t size) {
    return errno;
}
