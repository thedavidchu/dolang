#include <assert.h>
#include <stddef.h>

#include "common/common.h"
#include "arr/arr.h"
#include "tbl/tbl.h"

/* Define here rather than tbl.c */
#define INVALID (-1U)
#define TOMBSTONE (-2U)


static size_t tbl_gettableidx(const tbl *const restrict me, const void *const key, const bool return_tombstone, int *const err) {
    size_t hashcode = 0, table_home = 0, table_offset = 0, table_idx = 0, items_idx = 0;
    
    RETURN_IF_ERROR(me == NULL ? (*err = (int)ERROR_NULLPTR, true) : false, INVALID);
    RETURN_IF_ERROR(key == NULL ? (*err = (int)ERROR_NULLPTR, true) : false, INVALID);
    
    hashcode = me->hash_key(key);
    RETURN_IF_ERROR(me->cap == 0 ? (*err = (int)ERROR_DIVZERO, true) : false, INVALID);
    table_home = hashcode % me->cap;
    
    for (table_offset = 0; table_offset < me->cap; ++table_offset) {
        table_idx = (table_home + table_offset) % me->cap;
        items_idx = me->table[table_idx];
        
        if (items_idx == INVALID) {
            return table_idx;
        } else if (items_idx == TOMBSTONE) {
            if (return_tombstone) {
                return table_idx;
            }
            continue;
        } else {
            const tbl_kv *const item = arr_search(&me->items, items_idx);
            assert(item != NULL && "unexpected NULL item");
            if (item->hashcode != hashcode || me->key_cmp(item->key, key) != 0) {
                continue;
            }
            return table_idx;
        }
        
        assert(0 && "should not get here!");
    }
    
    /* No space and not found */
    return INVALID;
}
