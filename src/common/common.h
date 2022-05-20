/* A file containing the compatibility differences between compilers. */
#pragma once

#include <assert.h>
#include <errno.h>

/* Allow use of inline in this file, even if it is not valid. */
#ifndef __STDC_VERSION__
    /* NOTE: the user should not use either of these words */
    #define inline
    #define restrict
#endif

/** A check for function returns.
 * Inputs
 * ------
 * cond_ : int
 *     condition that is evaluated; a 'true' result will cause the 'err_' to return.
 * err_ : int (no side effects)
 *     error value to be returned if the condition is met.
 * Notes
 * -----
 * * cond_ is evaluated only once; err_ may be evaluated many times.
 */
#define RETURN_IF_ERROR(cond_, err_) do { \
    int _err = 0; /* err_ cannot be '_err'. */ \
    /* We cannot use strerror((err_)) because if err_ is an invalid errno, */ \
    /* then strerror may return NULL or may set errno. */ \
    if ((_err = (int)(cond_))) { \
        const int old_errno = errno; \
        errno = 0; /* Reset errno */ \
        /* We use this function so we do not need to include stdio.h. */ \
        _err = print_stderr("[ERROR] %s:%d: err_ = \"%s\" = %d: \"%s\"\n" \
                           "\tcond_ = \"%s\" = %d\n", \
                           __FILE__, __LINE__, #err_, (int)(err_), _safe_strerror((int)(err_)), \
                           #cond_, _err); \
        assert(_err == 0 && "failed to print error message to stderr"); \
        errno = old_errno; \
        return (int)(err_); \
    } \
} while (0)

#define REQUIRE_NO_ERROR(cond_, msg_) do { \
    int _err = 0; /* err_ cannot be '_err'. */ \
    if ((_err = (int)(cond_))) { \
        const int old_errno = errno; \
        errno = 0; /* Reset errno */ \
        /* We use this function so we do not need to include stdio.h. */ \
        _err = print_stderr("[FATAL] %s:%d: %s\n\tcond_ = \"%s\" = %d\n", \
                           __FILE__, __LINE__, (msg_), #cond_, _err); \
        assert(_err == 0 && "failed to print error message to stderr"); \
        errno = old_errno; \
        _exit_failure(); \
    } \
} while (0)

/** Private function to be used with RETURN_IF_ERROR macro. This safely prints
 * the error associated with $errnum. */
const char *_safe_strerror(const int errnum);

void _exit_failure(void);

/** Log to the stderr stream. */
int print_stderr(const char *const restrict format, ...);

typedef enum {
    /* Unspecified error */
    ERROR = -1,
    ERROR_FATAL = -2, /* Should abort */
    ERROR_UNIMPLEMENTED = -3, /* Should abort */

    /* Specific Errors */
    ERROR_NULLPTR = -1000,
    ERROR_OVERFLOW = -1001,
    ERROR_DIVZERO = -1002,
    ERROR_KEY = -1003,
    ERROR_VALUE = -1004,
    ERROR_STDOUT = -1005,
    ERROR_STDERR = -1006,
    ERROR_STDIN = -1007,
    ERROR_NOROOM = -1008,
} ErrorCode;
