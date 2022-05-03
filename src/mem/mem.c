#include <assert.h>
#include <errno.h>
#include <stdlib.h>

#include "common/common.h"
#include "mem/mem.h"


/** Test for errors:
    (1) errno is not set (error is unhandled),
    (2a) $me is NULL (big error!),
    (2b) *$me is not NULL (we may be over-writing memory) (OPTIONAL???), and
    (3) $num * $size is valid,
*/
static inline int is_error(void **const me, const size_t num, const size_t size);


static inline int is_error(void **const me, const size_t num, const size_t size) {
    size_t num_bytes = 0;

    if (errno) {
        return errno;
    }
    if (me == NULL) {
        return -1;
    }
    /* Check if either $num or $size are zero. If so, then we know that the
    number of bytes will be in the valid range, because it will be zero. We also
    do this check to ensure that we don't divide be zero in the next step. */
    if ((num_bytes = num * size) == 0) {
        return 0;
    }
    if (num != num_bytes / size) {
        return -1;
    }
    return 0;
}


int mem_malloc(void **const me, size_t num, size_t size) {
    int err = 0;
    size_t num_bytes = 0;

    if ((err = is_error(me, num, size))) {
        return err;
    }
    /* By convention, we assume that all non-initialized pointers are NULL. This
    will add verbosity, but prevent memory leaks. (Maybe? It will prevent
    memory leaks if we don't set pointers to NULL willy-nilly). */
    if (*me != NULL) {
        return -1;
    }
    if ((num_bytes = num * size) == 0) {
        *me = NULL;
        return 0;
    }
    if ((*me = malloc(num_bytes)) == NULL) {
        assert(errno && "errno is not set when malloc returned an error!");
        return errno;
    }
    assert(errno == 0 && "errno is set when malloc returned valid value!");
    return 0;
}

int mem_realloc(void **const me, size_t num, size_t size) {
    int err = 0;
    size_t num_bytes = 0;
    void *new_ptr = NULL;

    if ((err = is_error(me, num, size))) {
        return err;
    }
    if ((num_bytes = num * size) == 0) {
        if (*me == NULL) {
            /* I included this assertion to reinforce that *me is NULL. I under-
            stand that it is redundant, but assertions are removed when we
            compile in deployment mode. */
            assert(*me == NULL && "invalid pointer *me is non-NULL!");
            return 0;
        } else {
            err = mem_free(me);
            assert(err == errno && "returned error and errno do not match!");
            return err;
        }
    }
    if ((new_ptr = realloc(*me, num_bytes)) == NULL) {
        assert(errno && "errno is not set when malloc returned an error!");
        return errno;
    }
    assert(errno == 0 && "errno is set when malloc returned valid value!");
    *me = new_ptr;
    return 0;
}

int mem_free(void **const me) {
    int err = 0;
    
    if ((err = is_error(me, /*num=*/0, /*size=*/0))) {
        return err;
    }
    free(*me);
    /* If there is an error, we cannot guarantee that the memory was freed. */
    if (errno) {
        return errno;
    }
    *me = NULL;
    return 0;
}
