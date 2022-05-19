#include <assert.h>
#include <stddef.h>

#include "common/common.h"
#include "bool/bool.h"
#include "arr/arr.h"
#include "tbl/tbl.h"

/* Define here rather than tbl.c */
#define INVALID (-1U)
#define TOMBSTONE (-2U)


static int noop_dtor(void *const item);
static int noop_dtor(void *const item) {
    assert(item != NULL && "item is NULL!");
    return 0;
}


static int tbl_gettableidx(const tbl *const restrict me, const void *const key, const bool return_tombstone, size_t *const table_idx_p) {

    size_t hashcode = 0, table_home = 0, table_offset = 0, table_idx = 0, items_idx = 0;
    
    RETURN_IF_ERROR(me == NULL, ERROR_NULLPTR);
    RETURN_IF_ERROR(key == NULL, ERROR_NULLPTR);
    RETURN_IF_ERROR(table_idx_p == NULL, ERROR_NULLPTR);
    
    hashcode = me->hash_key(key);
    RETURN_IF_ERROR(me->cap == 0, ERROR_DIVZERO);
    table_home = hashcode % me->cap;
    
    for (table_offset = 0; table_offset < me->cap; ++table_offset) {
        table_idx = (table_home + table_offset) % me->cap;
        items_idx = me->table[table_idx];
        
        if (items_idx == INVALID) {
            *table_idx_p = table_idx;
            return 0;
        } else if (items_idx == TOMBSTONE) {
            if (return_tombstone) {
                *table_idx_p = table_idx;
                return 0;
            }
            continue;
        } else {
            const tbl_kv *const item = arr_search(&me->items, items_idx);
            assert(item != NULL && "unexpected NULL item");
            if (item->hashcode != hashcode || me->key_cmp(item->key, key) != 0) {
                continue;
            }
            *table_idx_p = table_idx;
            return 0;
        }
        
        assert(0 && "should not get here!");
    }
    
    /* No space and not found */
    return ERROR;
}
