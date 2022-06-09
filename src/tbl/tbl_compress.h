#pragma once

#include <assert.h>

#include "mem/mem.h"
#include "tbl/tbl.h"
#include "tbl/tbl_helper.h" /* For TOMBSTONE and INVALID */

/* Erase the table by adding -1 everywhere. */
static void tbl_erasetable_nocheck(tbl *const me) {
    size_t i = 0;

    /* Can probably be optimized with memset */
    for (i = 0; i < me->cap; ++i) {
        me->table[i] = (size_t)(-1);
    }

    return;
}

/* Try finding an empty table index. This should probably be introduced to the
 * other functions to cut out redundancy. Actually, this may not be the best
 * idea because we can only guarantee that there are no tombstones here. */
static size_t tbl_getemptytableidx_nocheck(tbl *const me,
                                           const tbl_kv *const item) {
    size_t home = item->hashcode % me->cap, offset = 0;

    /* Assuming me->cap != 0 */
    for (offset = 0; offset < me->cap; ++offset) {
        size_t table_idx = (home + offset) % me->cap;

        if (me->table[table_idx] == INVALID ||
            me->table[table_idx] == TOMBSTONE) {
            return table_idx;
        }
    }

    return INVALID;
}

/** Compress the items in the table.

Notes
-----
1. For now, we will leave the table and items arrays the same length.
*/
static int tbl_compressitems(tbl *const me) {
    size_t dst = 0, src = 0, items_idx = 0;
    for (src = 0; src < me->items.len; ++src) {
        const tbl_kv *const restrict tbl_item =
            (tbl_kv *)arr_search(&me->items, src);

        /* Skip copying to oneself */
        if (src == dst) {
            continue;
        }
        /* Skip empty items */
        if (tbl_item->hashcode == 0 && (tbl_item->key == NULL ||
            tbl_item->value == NULL)) {
            assert(tbl_item->hashcode == 0 &&
                   tbl_item->key == NULL & tbl_item->value == NULL);
            continue;
        }

        /* Copy items src -> dst */
        mem_memcpy(arr_search(&me->items, src), arr_search(&me->items, dst), 1,
                   sizeof(tbl_kv));

        /* TODO(dchu): zero out src */
        assert(0 && "TODO");

        ++dst;
    }

    /* Rehash all the items */
    tbl_erasetable_nocheck(me);

    for (items_idx = 0; items_idx < me->items.len; ++items_idx) {
        const size_t table_idx =
            tbl_getemptytableidx_nocheck(me, arr_search(&me->items, items_idx));

        assert(table_idx != INVALID &&
               "this can't be possible, because we just shrank the items list");
        me->table[table_idx] = items_idx;
    }

    return 0;
}
