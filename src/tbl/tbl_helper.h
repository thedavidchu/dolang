#include <assert.h>
#include <stddef.h>

#include "src/arr/arr.h"
#include "src/bool/bool.h"
#include "src/common/common.h"
#include "src/tbl/tbl.h"

/* Define here rather than tbl.c */
#define INVALID ((size_t)(-1))
#define TOMBSTONE ((size_t)(-2))

/** Item destructor for the array in the table. This is a no-op. */
static int arr_noop_dtor(void *const item);
/** Print an item_idx (0, ..., TOMBSTONE, INVALID). */
static inline int item_idx_print(const size_t item_idx);
static int tbl_gettableidx(const tbl *const restrict me, const void *const key,
                           const bool return_tombstone,
                           size_t *const table_idx_p);

static int arr_noop_dtor(void *const item) {
    assert(item != NULL && "item is NULL!");
    return 0;
}

static inline int item_idx_print(const size_t item_idx) {
    int err = 0;

    switch (item_idx) {
    case (INVALID):
        err = fputs("INVALID", stdout);
        RETURN_IF_ERROR(err == EOF, ERROR_STDOUT);
        return 0;
    case (TOMBSTONE):
        err = fputs("TOMBSTONE", stdout);
        RETURN_IF_ERROR(err == EOF, ERROR_STDOUT);
        return 0;
    default:
        err = printf("%zu", item_idx);
        RETURN_IF_ERROR(err < 0, ERROR_STDOUT);
        return 0;
    }
}

/** Get the table index that the key has (or would have if it is not present).
 *
 * This has two different modes.
 * 1. Insert: search for the key as if it is already in the array. Stop when we
 * have searched the entire table. If it is not in the array, then return the
 * first TOMBSTONE (or error if no tombstone).
 * 2. Search/Remove: search for the key as if it is already in the array. Not
 * finding the key is not an error. We skip over tombstones and do not need to
 * track them.
 */
static int tbl_gettableidx(const tbl *const restrict me, const void *const key,
                           const bool return_tombstone,
                           size_t *const table_idx_p) {

    size_t first_tombstone = INVALID, hashcode = 0, table_home = 0,
           table_offset = 0;

    /* Optimization: remove these and indicate that this function performs no
    checks. */
    RETURN_IF_ERROR(me == NULL, ERROR_NULLPTR);
    RETURN_IF_ERROR(key == NULL, ERROR_NULLPTR);
    RETURN_IF_ERROR(table_idx_p == NULL, ERROR_NULLPTR);
    RETURN_IF_ERROR(me->cap == 0, ERROR_DIVZERO);

    hashcode = me->hash_key(key);
    table_home = hashcode % me->cap;

    for (table_offset = 0; table_offset < me->cap; ++table_offset) {
        const size_t table_idx = (table_home + table_offset) % me->cap;
        const size_t items_idx = me->table[table_idx];

        if (items_idx == INVALID) { /* key not present */
            *table_idx_p = table_idx;
            return 0;
        } else if (items_idx == TOMBSTONE) {
            /* Record first instance of tombstone in table. We will fall
            back to this if necessary. */
            if (return_tombstone && first_tombstone == INVALID) {
                first_tombstone = table_idx;
            }
            /* Otherwise, treat it like an item not equal to the key we're
            searching for. */
            continue;
        } else {
            /* We use an if-else ladder because we wish to declare a variable
            within the else-clause. */
            const tbl_kv *const item = arr_search(&me->items, items_idx);

            assert(item != NULL && "unexpected NULL item");
            if (item->hashcode == hashcode &&
                me->key_cmp(item->key, key) == 0) { /* key present */
                *table_idx_p = table_idx;
                return 0;
            }
            continue;
        }
    }

    if (return_tombstone && first_tombstone == INVALID) {
        /* No space and not found */
        return ERROR_NOROOM;
    }
    /* Account for very weird corner case. If have no INVALID or matching items
    but we have tombstones, we will have space to insert. */
    if (return_tombstone) {
        *table_idx_p = first_tombstone;
        return 0;
    } else {
        *table_idx_p = INVALID;
        return 0;
    }
}
