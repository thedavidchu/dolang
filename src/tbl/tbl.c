#include "common/common.h"
#include "mem/mem.h"
#include "arr/arr.h"

#include "tbl/tbl.h"


static int noop_dtor(void *const item);
static int noop_dtor(void *const item) {
    assert(item != NULL && "item is NULL!");
    return 0;
}


int tbl_ctor(tbl *const restrict me, size_t cap,
        size_t (*hash_key)(const void *const restrict),
        int (*key_dtor)(void *const restrict),
        int (*value_dtor)(void *const restrict)) {
    int err = 0;

    RETURN_IF_ERROR((err = mem_malloc(&me->table, cap, sizeof *me->table)), err);
    RETURN_IF_ERROR((err = arr_ctor(&me->items, cap, sizeof(tbl_kv))), err);
    me->cap = cap;

    me->hash_key = hash_key;
    me->key_dtor = key_dtor;
    me->value_dtor = value_dtor;
    return 0;
}

int tbl_dtor(tbl *const restrict me) {
    int err = 0, err_tmp = 0;
    size_t i = 0;
    tbl_kv *item = NULL;

    /* Ugh C doesn't have closure... so I can't create a function to delete the
    key/value pairs. */
    /* Delete array keys/values*/
    for (i = 0; i < me->len; ++i) {
        item = (tbl_kv *)arr_search(&me->items, i);
        me->key_dtor(item->key);
        me->value_dtor(item->value);
    }

    /* We want to free as much as we can before returning, so we hold a
    temporary error value before checking if the other structure returns an
    error. */
    err_tmp = arr_dtor(&me->items, noop_dtor);
    RETURN_IF_ERROR((err = mem_free(&me->table)), err);
    if (err_tmp) {
        return err_tmp;
    }

    return 0;
}

int tbl_insert(tbl *const restrict me, const void *const key, void *const value);
void *tbl_search(tbl *const restrict me, const void *const key);
int tbl_remove(tbl *const restrict me, const void *const key);
