/*! In each of these functions, important tests are:
    (1) errno is not set (error is unhandled),
    (2) $me is NULL (big error!), and
    (3) $num * $size is valid,
*/

#include <assert.h>
#include <errno.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "common/common.h"
#include "mem/mem.h"


/*! Check that $num * $size is valid. */
static inline int is_overflow(const size_t num, const size_t size);


static inline int is_overflow(const size_t num, const size_t size) {
    size_t num_bytes = 0;
    
    /* Check if either $num or $size are zero. If so, then we know that the
    number of bytes will be in the valid range, because it will be zero. We also
    do this check to ensure that we don't divide be zero in the next step. */
    if ((num_bytes = num * size) == 0) {
        return 0;
    } else if (num != num_bytes / size) {
        return -1;
    }
    return 0;
}

/******************************************************************************/

int mem_malloc(void **const me, size_t num, size_t size) {
    int err = 0;
    size_t num_bytes = 0;

    RETURN_IF_ERROR((err = errno) || (err = is_overflow(num, size)), err);
    /* By convention, we assume that all non-initialized pointers are NULL. This
    will add verbosity, but prevent memory leaks. (Maybe? It will prevent
    memory leaks if we don't set pointers to NULL willy-nilly). */
    RETURN_IF_ERROR(me == NULL || *me != NULL, -1);
    /* We specifically enumerate the 0 case, because we want to ensure that
    calls to mem_malloc(ptr, 0, 0) return NULL and avoid malloc return NULL
    without setting an error. */
    if ((num_bytes = num * size) == 0) {
        *me = NULL;
        return 0;
    }
    if ((*me = malloc(num_bytes)) == NULL) {
        #ifndef VALGRIND
            assert(errno != 0 && "errno is not set when malloc returns an error");
        #else
            /* Valgrind does not set errno */
            RETURN_IF_ERROR(errno != 0, ENOMEM);
        #endif
        return errno;
    }
    assert(errno == 0 && "errno is set when malloc returned valid value!");
    return 0;
}

int mem_realloc(void **const me, size_t num, size_t size) {
    int err = 0;
    size_t num_bytes = 0;
    void *new_ptr = NULL;

    RETURN_IF_ERROR((err = errno) || (err = is_overflow(num, size)), err);
    RETURN_IF_ERROR(0, err);
    RETURN_IF_ERROR(me == NULL, -1);
    if ((num_bytes = num * size) == 0) {
        if (*me == NULL) {
            return 0;
        } else {
            err = mem_free(me);
            assert(err == errno && "returned error and errno do not match!");
            return err;
        }
    }
    if ((new_ptr = realloc(*me, num_bytes)) == NULL) {
        #ifndef VALGRIND
            assert(errno != 0 && "errno is not set when realloc returns an error");
        #else
            /* Valgrind does not set errno */
            RETURN_IF_ERROR(errno != 0, ENOMEM);
        #endif
        return errno;
    }
    assert(errno == 0 && "errno is set when malloc returned valid value!");
    *me = new_ptr;
    return 0;
}

int mem_free(void **const me) {
    RETURN_IF_ERROR(errno, errno);
    RETURN_IF_ERROR(me == NULL, -1);
    free(*me);
    /* If there is an error, we cannot guarantee that the memory was freed. */
    RETURN_IF_ERROR(errno, errno);

    *me = NULL;
    return 0;
}


int mem_memcpy(const void *const restrict src, void *const restrict dst, const size_t num, const size_t size) {
    int err = 0;
    const void *dst_ = NULL;

    if ((err = errno) || (err = is_overflow(num, size))) {
        return err;
    } else if (src == NULL || dst == NULL) {
        return -1;
    }
    if ((dst_ = memcpy(dst, src, num * size)) == NULL || errno) {
        assert(dst_ == NULL && errno &&
            "error return and error code are mismatched!");
        return errno;
    }
    assert(dst_ != NULL && errno == 0 &&
        "no error returned but error code claims error!");
    return 0;
}

int mem_memmove(const void *const src, void *const dst, const size_t num, const size_t size) {
    int err = 0;
    const void *dst_ = NULL;
    
    if ((err = errno) || (err = is_overflow(num, size))) {
        return err;
    } else if (src == NULL || dst == NULL) {
        return -1;
    }
    if ((dst_ = memmove(dst, src, num * size)) == NULL || errno) {
        assert(dst_ == NULL && errno &&
            "error return and error code are mismatched!");
        return errno;
    }
    assert(dst_ != NULL && errno == 0 &&
        "no error returned but error code claims error!");
    return 0;
}

