#include <errno.h>
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
        errno = old_errno;
    }

    return s;
}