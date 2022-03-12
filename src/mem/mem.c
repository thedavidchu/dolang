#include <assert.h>
#include <stdlib.h>
#include <errno.h>

#include "mem.h"

/* NOTE(dchu): Assumes that implicit conversion to int is legal. This is not
to be used exernally, which is why it  is not in mem.h. */
enum custom_error {
    PTR_IS_NULL = -10, PTR2NULL = -11
};

int mem_new(void **const p, const size_t size) {
    /* Check for unhandled errors. */
    if (errno) {
        /* assert(!errno && "unhandled error before malloc."); */
        return errno;
    }

    /* Check for NULL passed in */
    if (!p) {
        return (int)PTR_IS_NULL;
    }

    if (!size) {    /* This is probably an error */
        *p = NULL;
        return 0;
    }
    /* We do not check if there is already a value, so this may overwrite values */
    if (!(*p = malloc(size))) {
        /* *p is NULL becasue of malloc. Check that errno != 0; if errno = 0,
        then something fishy is going on, so return -1. */
        return errno ? errno : -1;
    }
    /* Ok! *p is a valid pointer => errno = 0 */
    return 0;
}

int mem_del(void **const p) {
    /* Check for unhandled errors. */
    if (errno) {
        /* assert(!errno && "unhandled error before free."); */
        return errno;
    }

    /* Check for NULL passed in */
    if (!p) {
        return (int)PTR_IS_NULL;
    }

    if (*p) {
        free(*p);
        if (!errno) {
            *p = NULL;
        }
    }   /* Otherwise *p == NULL, and errno = 0 presumably */
    return errno;
}

int mem_resize(void **const p, const size_t size) {
    void *temp;

    /* Check for unhandled errors. */
    if (errno) {
        /* assert(!errno && "unhandled error before malloc."); */
        return errno;
    }

    /* Check for NULL passed in */
    if (!p) {
        return (int)PTR_IS_NULL;
    }

    if (*p == NULL && !size) {  /* This is probably an error */
        return 0;
    } else if (*p == NULL) {
        return mem_new(p, size);
    } else if (!size) {
        return mem_del(p);
    }

    /* Actually do the resize */
    if (!(temp = realloc(*p, size))) {
        /* *temp is NULL becasue of realloc. Check that errno != 0; if errno = 0,
        then something fishy is going on, so return -1. */
        return errno ? errno : -1;
    } else {
        *p = temp;
    }
    return errno;
}
