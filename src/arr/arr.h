#pragma once

#include <stddef.h>

#include "common/common.h"


typedef struct {
    void *items;    /* Pointer to the items. This is a void* so that it is
                       a generic pointer and the user avoids the urge to
                       directly index from it (you can't). */
    size_t len;     /* Number of items */
    size_t cap;     /* Number of spaces for items */
    size_t size;    /* Size of each item in bytes */
} arr;

/* TODO(dchu): if cap == 0, set to minimum size. Also, ensure below max size. */
int arr_ctor(arr *const me, const size_t cap, const size_t size);
int arr_dtor(arr *const me, int (*item_dtor)(void *const));

/* Ensure below max size. */
int arr_insert(arr *const me, const size_t idx, void *const item);
void *arr_search(const arr *const me, const size_t idx);
int arr_change(const arr *const me, const size_t idx, void *const restrict item, int (*item_dtor)(void *const));
int arr_remove(arr *const me, const size_t idx, int (*item_dtor)(void *const));

int arr_append(arr *const me, void *const item);
int arr_pop(arr *const me, int (*item_dtor)(void *const));

int arr_stderr(const arr *const me, int (*item_stderr)(const void *const));
