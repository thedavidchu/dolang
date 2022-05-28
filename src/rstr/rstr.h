/** TODO(dchu): 
 * 1. Make print functions print non-printable characters nicely.
*/

#pragma once

#include <stddef.h>

typedef struct {
    const char *str;
    size_t len;
} rstr;

/** Construct an rstr from a constant C string. Note that this C string must be
 * constant for its lifetime too; otherwise we may inadvertently change the
 * string in the rstr. */
int rstr_ctor(rstr *const restrict me, const char *const str, const size_t len);
int rstr_dtor(rstr *const restrict me, int (*str_dtor)(char *const));
int rstr_slice(const rstr *const me, const size_t start, const size_t end, rstr *const result);

/** Sort the rstr in order.
 * 
 * The ordering is applied as follows:
 * 1. NULL < valid string (NULL == NULL)
 * 2. shorter string < longer string
 * 3. strncmp
 * 
 * Notes
 * -----
 * 1. I feel like I should be able to add `restrict` to the parameters. While
 * the are not guaranteed not to overlap, I do not see how pointer aliasing
 * could negatively affect this, because it is a read-only function. Why I did
 * not add `restrict` was because the compiler could theoretically assume that
 * me != other, and skip the first test erroneously.
 * */
int rstr_cmp(const rstr *const me, const rstr *const other);
int rstr_debug(const rstr *const restrict me);
int rstr_print(const rstr *const restrict me);
