#include <assert.h>
#include <errno.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h> /* exit() */
#include <string.h> /* strerror, NULL */

#include "common/common.h"

const char *_safe_strerror(const int errnum) {
    static const char *const UNKNOWN_ERROR = "unknown error";
    const char *s = NULL;
    const int old_errno = errno;

    errno = 0; /* Reset errno */
    /* This standardizes unknown errors. Unknown errors that return a valid string but set errno are changed to a standard error. */
    if ((s = strerror(errnum)) == NULL || errno) {
        s = UNKNOWN_ERROR;
    }
    errno = old_errno;

    return s;
}

void _exit_failure(void) {
    exit(EXIT_FAILURE);
    assert(0 && "failed to exit");
}


int print_stderr(const char *const restrict format, ...) {
    int err = 0;
    va_list ap;
    const int old_errno = errno;

    va_start(ap, format);
    errno = 0;
    if (vfprintf(stderr, format, ap) < 0) {
        assert((err = errno) && "no error message upon failure!");
    } else {
        assert((err = errno) == 0 && "error message upon pass!");
    }
    va_end(ap);
    errno = old_errno;
    return err;
}