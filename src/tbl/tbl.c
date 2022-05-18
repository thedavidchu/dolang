#include <assert.h>

#include "common/common.h"
#include "mem/mem.h"
#include "arr/arr.h"

#include "tbl/tbl.h"
#include "tbl/tbl_helper.h" /* Define INVALID and TOMBSTONE */


static int noop_dtor(void *const item);
static int noop_dtor(void *const item) {
    assert(item != NULL && "item is NULL!");
    return 0;
}


int tbl_ctor(tbl *const restrict me, size_t cap,
        size_t (*hash_key)(const void *const restrict),
        int (*key_cmp)(const void *const restrict, const void *const restrict)) {
    int err = 0;

    if (me == NULL) {
        return (int)ERROR_NULLPTR;
    }
    RETURN_IF_ERROR((err = mem_malloc((void **)&me->table, cap, sizeof *me->table)), err);
    RETURN_IF_ERROR((err = arr_ctor(&me->items, cap, sizeof(tbl_kv))), err);
    me->cap = cap;

    me->hash_key = hash_key;
    me->key_cmp = key_cmp;
    return 0;
}

int tbl_dtor(tbl *const restrict me, int (*key_dtor)(void *const restrict),
        int (*value_dtor)(void *const restrict)) {
    int err = 0, err_tmp = 0;
    size_t i = 0;
    tbl_kv *item = NULL;

    if (me == NULL) {
        return (int)ERROR_NULLPTR;
    }

    /* Ugh C doesn't have closure... so I can't create a function to delete the
    key/value pairs. */
    /* Delete array keys/values*/
    for (i = 0; i < me->len; ++i) {
        item = (tbl_kv *)arr_search(&me->items, i);
        key_dtor(item->key);
        value_dtor(item->value);
    }

    /* We want to free as much as we can before returning, so we hold a
    temporary error value before checking if the other structure returns an
    error. */
    err_tmp = arr_dtor(&me->items, noop_dtor);
    RETURN_IF_ERROR((err = mem_free((void **)&me->table)), err);
    if (err_tmp) {
        return err_tmp;
    }

    return 0;
}

int tbl_insert(tbl *const restrict me, void *const key, void *const value, int (*value_dtor)(void *const restrict)) {
    size_t hashcode = 0, home = 0, offset = 0;
    int err = 0;

    /* This would be when C99 would be great. We could error check and then
    declar the hashcode as const below this check. */
    if (me == NULL || key == NULL || value == NULL) {
        return (int)ERROR_NULLPTR;
    }
    
    hashcode = me->hash_key(key);   /* const */
    if (me->cap == 0) {
        return (int)ERROR_DIVZERO;
    }
    home = hashcode % me->cap;  /* const */

    for (offset = 0; offset <= me->cap; ++offset) {
        const size_t probe = (home + offset) % me->cap;
        const size_t arr_idx = me->table[probe];
        tbl_kv *item_p = NULL;
        if (arr_idx == INVALID || arr_idx == TOMBSTONE) {
            /* Not found => insert */
            tbl_kv item = {hashcode, key, value};
            size_t new_arr_idx = me->items.len;

            /* TODO(dchu): expand if necessary. */
            me->table[probe] = new_arr_idx;
            assert(arr_search(&me->items, new_arr_idx) == NULL &&
                    "item already where we will place new item!");
            RETURN_IF_ERROR(err = arr_append(&me->items, &item), err);
            return 0;
        }

        item_p = (tbl_kv *)arr_search(&me->items, arr_idx);
        assert(item_p != NULL && "unexpected NULL");
        if (me->key_cmp(item_p->key, key) != 0) {
            continue;
        }
        assert(value_dtor(item_p->value) == 0 && "failed to destroy old value");
        item_p->value = value;
        return 0;        
    }

    assert(0 && "no empty space in the hash table");
}

void *tbl_search(tbl *const restrict me, const void *const key) {
    size_t table_idx = INVALID, items_idx = INVALID;
    tbl_kv *item;
    if (me == NULL || key == NULL) {
        return NULL;
    }
    
    RETURN_IF_ERROR((table_idx = tbl_gettableidx(me, key, false)) == INVALID, NULL);
    items_idx = me->table[table_idx];
    RETURN_IF_ERROR((item = arr_search(&me->items, items_idx)) == NULL, NULL);
    
    return item->value;
}
int tbl_remove(tbl *const restrict me, const void *const key, int (*key_dtor)(void *const restrict), int (*value_dtor)(void *const restrict)) {
    if (me == NULL || key == NULL) {
        return (int)ERROR_NULLPTR;
    }

    /* RETURN_IF_ERROR(item = tbl_gettableidx(me, key), -1); */
    assert(key_dtor(NULL) == 0 && "key destroy failed");
    assert(value_dtor(NULL) == 0 && "value destroy failed");

    return 0;
}
