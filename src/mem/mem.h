#pragma once

/** Allocate memory to a pointer (if possible) or return an error value and NULL
if the allocation cannot be done. */
int mem_malloc(void **const me, const size_t num, const size_t size);

/** Resize a (assumed-to-be) valid pointer (if possible) and keep the old
pointer and return an error value if the resize cannot be done.

Possibilities:
* If $me == NULL, then return an error. Otherwise, $me is valid, so we proceed.

                | *me == NULL                   | *me != NULL (assumed valid)
--------------------------------------------------------------------------------
num * size      | Call      : (no op)           | Call      : free()
    is zero (0) | Set *me   : NULL (untouched)  | Set *me   : ptr -> NULL
                | Return    : 0                 | Return    : 0
--------------------------------------------------------------------------------
num * size      | Call      : realloc()         | Call      : realloc()
    is valid    | Set *me   : NULL -> ptr       | Set *me   : ptr -> ptr
                | Return    : 0                 | Return    : 0
--------------------------------------------------------------------------------
num * size      | Call      : realloc()         | Call      : Realloc()
    is too big  | Set *me   : NULL (untouched)  | Set *me   : (untouched)
                | Return    : ENOMEM            | Return    : ENOMEM
--------------------------------------------------------------------------------
num * size      | Call      : (no op)           | Call      : (no op)
    overflows   | Set *me   : NULL (untouched)  | Set *me   : (untouched)
                | Return    : -1                | Return    : -1
--------------------------------------------------------------------------------
*/
int mem_realloc(void **const me, const size_t num, const size_t size);

/** Free a (assumed-to-be) valid pointer and set it to NULL. */
int mem_free(void **const me);
