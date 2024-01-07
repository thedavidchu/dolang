#pragma once

#include <stddef.h>

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