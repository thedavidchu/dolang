#include <ctype.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>

#include <common/common.h>

#include "rstr/rstr.h"


int rstr_ctor(rstr *const restrict me, const char *const str, const size_t len) {
    RETURN_IF_ERROR(me == NULL, ERROR_NULLPTR);
    me->str = str;
    me->len = len;
    return 0;
}

int rstr_dtor(rstr *const restrict me, int (*str_dtor)(char *const)) {
    RETURN_IF_ERROR(me == NULL, 0); /* Successfully freed NULL by default. */
    /* We discard the const qualifier upon destruction. */
    REQUIRE_NO_ERROR(str_dtor((char *)me->str), "failed to free string");
    me->str = NULL;
    me->len = 0;
    return 0;
}

int rstr_slice(const rstr *const me, const size_t start, const size_t end, rstr *const result) {
    RETURN_IF_ERROR(me == NULL, ERROR_NULLPTR);
    RETURN_IF_ERROR(me->str == NULL, ERROR_NULLPTR);
    RETURN_IF_ERROR(start > end, ERROR_OUTOFBOUNDS);
    RETURN_IF_ERROR(end > me->len, ERROR_OUTOFBOUNDS);
    result->str = &me->str[start];
    result->len = end - start;
    return 0;
}

int rstr_cmp(const rstr *const me, const rstr *const other) {
    if (me == other) {
        return 0;
    }

    if (me == NULL && other != NULL) {
        return -1;
    }
    /* If me is not expected to be NULL, then flipping this may yield speed ups */
    if (me != NULL && other == NULL) {
        return 1;
    }
    
    if (me->len < other->len) {
        return -1;
    }
    if (me->len > other->len) {
        return 1;
    }
    /* We know that they are the same length slice, so we can compare the
    pointers directly. This also deals with the NULL case in the case that the
    lengths are zero. */
    if (me->str == other->str) {
        return 0;
    }
    return strncmp(me->str, other->str, me->len);
}

int rstr_debug(const rstr *const restrict me) {
    int r = 0;

    RETURN_IF_ERROR(me == NULL, ERROR_NULLPTR);
    RETURN_IF_ERROR(me->str == NULL, ERROR_NULLPTR);
    RETURN_IF_ERROR(me->len > (size_t)INT_MAX, ERROR_OUTOFBOUNDS);

    r = printf("(len=%d)'%.*s'\n", (int)me->len, (int)me->len, me->str);
    return (r < 0) ? ERROR : 0;

}

int rstr_print(const rstr *const restrict me) {
    int r = 0;

    RETURN_IF_ERROR(me == NULL, ERROR_NULLPTR);
    RETURN_IF_ERROR(me->str == NULL, ERROR_NULLPTR);
    RETURN_IF_ERROR(me->len > (size_t)INT_MAX, ERROR_OUTOFBOUNDS);

    r = printf("'%.*s'\n", (int)me->len, me->str);
    return (r < 0) ? ERROR : 0;
}