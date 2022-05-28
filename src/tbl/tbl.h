#pragma once

#include <stddef.h>

#include "arr/arr.h"

typedef struct {
    size_t *table;
    size_t len; /* Number of elements in the table. */
    size_t cap; /* Number of total spots available in the table. */
    size_t (*hash_key)(const void *const restrict);
    int (*key_cmp)(const void *const restrict, const void *const restrict);
    arr items;
} tbl;

typedef struct {
    size_t hashcode;
    void *key; /* Must NOT change. Either pointer or its value. */
    void *value;
} tbl_kv;

int tbl_ctor(tbl *const restrict me, size_t cap,
             size_t (*hash_key)(const void *const restrict),
             int (*key_cmp)(const void *const restrict,
                            const void *const restrict));
int tbl_dtor(tbl *const restrict me, int (*key_dtor)(void *const restrict),
             int (*value_dtor)(void *const restrict));

int tbl_insert(tbl *const restrict me, void *const key, void *const value,
               int (*value_dtor)(void *const restrict));
void *tbl_search(tbl *const restrict me, const void *const key);
int tbl_remove(tbl *const restrict me, const void *const key,
               int (*key_dtor)(void *const restrict),
               int (*value_dtor)(void *const restrict));

int tbl_print(const tbl *const me, int (*key_print)(const void *const),
              int (*value_print)(const void *const));
