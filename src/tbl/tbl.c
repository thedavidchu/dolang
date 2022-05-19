#include <assert.h>
#include <stdio.h>

#include "common/common.h"
#include "mem/mem.h"
#include "arr/arr.h"

#include "tbl/tbl.h"
#include "tbl/tbl_helper.h" /* Define INVALID and TOMBSTONE */


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
        ++me->len;
        assert(me->items.len == new_item_idx + 1 && "unexpected length of items");
        return 0;
    } else {
        tbl_kv *const item_p = (tbl_kv *)arr_search(&me->items, item_idx);
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
    
    if (me == NULL || key == NULL) {
        return NULL;
    }
    if ((err = tbl_gettableidx(me, key, false, &table_idx))) {
        return NULL;
    }
    if (table_idx == INVALID) {
        return NULL;
    }
    assert(table_idx < me->cap && "table_idx out of range!");
    items_idx = me->table[table_idx];
    if ((item = arr_search(&me->items, items_idx)) == NULL) {
        return NULL;
    }
    return item->value;
}

int tbl_remove(tbl *const restrict me, const void *const key, int (*key_dtor)(void *const restrict), int (*value_dtor)(void *const restrict)) {
    int err = 0;
    size_t table_idx = INVALID, item_idx = INVALID;
    tbl_kv *item = NULL;

    RETURN_IF_ERROR(me == NULL || key == NULL, ERROR_NULLPTR);

    RETURN_IF_ERROR(err = tbl_gettableidx(me, key, 
            /*return_tombstone=*/false, &table_idx), err);
    if (table_idx == INVALID) {
        return 0;
    }
    assert(table_idx < me->cap && "table_idx out of range!");
    item_idx = me->table[table_idx];
    RETURN_IF_ERROR((item = arr_search(&me->items, item_idx)) == NULL, ERROR);

    if ((err = key_dtor(item->key))) {
        int err_value = value_dtor(item->value);
        /* Set value to NULL if no error deleting it. */
        if (!err_value) {
            item->value = NULL;
        }
        return err;
    }
    RETURN_IF_ERROR(err = value_dtor(item->value), err);
    --me->len;
    item->hashcode = 0;
    item->key = NULL;
    item->value = NULL;

    /* TODO(dchu): shrink if necessary. */
    return 0;
}

int tbl_print(const tbl *const me, int (*key_print)(const void *const), int (*value_print)(const void *const)) {
    int err = 0;
    size_t i = 0;
    
    printf("(len = %zu, cap = %zu) [", me->len, me->cap);
    for (i = 0; i < me->cap; ++i) {
        if (me->table[i] == INVALID) {
            printf("INVALID");
        } else if (me->table[i] == TOMBSTONE) {
            printf("TOMBSTONE");
        } else {
            printf("%zu", me->table[i]);
        }
        printf("%s", i + 1 == me->cap ? "" : ", ");
    }
    printf("] ");

    printf("(len = %zu, cap = %zu) {", me->items.len, me->items.cap);
    for (i = 0; i < me->items.cap; ++i) {
        const tbl_kv *const item = (tbl_kv *)arr_search(&me->items, i);
        assert(item != NULL && "unexpected NULL");

        if (item->hashcode == 0 || item->key == NULL || item->value == NULL) {
            assert(item->hashcode == 0 && item->key == NULL &&
                    item->value == NULL && "expected all to be empty");
            continue;
        }
        printf("(%zu)", item->hashcode);
        err = key_print(item->key);
        assert(!err && "error printing key");
        err = value_print(item->value);
        assert(!err && "error printing value");

        printf("%s", i + 1 == me->items.cap ? "" : ", ");
    }
    printf("}");

    return 0;
}

