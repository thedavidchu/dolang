#pragma once

#include <stddef.h>

#include "arr/arr.h"


typedef struct {
    size_t *table;
    size_t len;
    size_t cap;
    size_t (*hash_key)(const void *const restrict);
    int (*key_cmp)(const void *const restrict, const void *const restrict);
    arr items;
} tbl;

typedef struct {
    size_t hashcode;
    const void *key;  /* Must NOT change. Either pointer or its value. */
    void *value;
} tbl_kv;

int tbl_ctor(tbl *const restrict me, size_t cap, size_t (*hash_key)(const void *const restrict), int (*key_cmp)(const void *const restrict, const void *const restrict));
int tbl_dtor(tbl *const restrict me, int (*key_dtor)(void *const restrict), int (*value_dtor)(void *const restrict));

int tbl_insert(tbl *const restrict me, const void *const key, void *const value, int (*value_dtor)(void *const restrict));
void *tbl_search(tbl *const restrict me, const void *const key);
int tbl_remove(tbl *const restrict me, const void *const key, int (*key_dtor)(void *const restrict), int (*value_dtor)(void *const restrict));

int tbl_stderr(const arr *const me, int (*key_stderr)(const void *const), int (*value_stderr)(const void *const));