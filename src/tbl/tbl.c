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
    int err = 0;
    size_t table_idx = INVALID, item_idx = INVALID;

    /* This would be when C99 would be great. We could error check and then
    declar the hashcode as const below this check. */
    RETURN_IF_ERROR(me == NULL || key == NULL || value == NULL, ERROR_NULLPTR);
    RETURN_IF_ERROR(me->cap == 0, ERROR_DIVZERO);
    
    RETURN_IF_ERROR(err = tbl_gettableidx(me, key, /*return_tombstone=*/true, &table_idx), err);
    item_idx = me->table[table_idx];
    if (item_idx == INVALID || item_idx == TOMBSTONE) {
        const size_t hashcode = me->hash_key(key), new_item_idx = me->items.len;
        tbl_kv item = {hashcode, key, value};
        
        /* TODO(dchu): expand/compress items if necessary */
        me->table[table_idx] = new_item_idx;
        assert(arr_search(&me->items, new_item_idx) == NULL &&
                "another item already exists where we will place the new item!");
        RETURN_IF_ERROR(err = arr_append(&me->items, &item), err);
        assert(me->items.len == new_item_idx + 1 && "unexpected length of items");
        return 0;
    } else {
        tbl_kv *const item_p = (tbl_kv *)arr_search(&me->items, arr_idx);
        assert(item_p != NULL && "unexpected NULL");
        assert(value_dtor(item_p->value) == 0 && "failed to destroy old value");
        item_p->value = value;
        return 0;
    }
}

void *tbl_search(tbl *const restrict me, const void *const key) {
    int err = 0;
    size_t table_idx = INVALID, items_idx = INVALID;
    tbl_kv *item;
    
    RETURN_IF_ERROR(me == NULL || key == NULL, NULL);
    RETURN_IF_ERROR(err = tbl_gettableidx(me, key, false, &table_idx), NULL);
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
