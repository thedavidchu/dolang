#pragma once

#include <stddef.h>

#include "src2/common/common.h"


typedef struct {
    void *items;    /* Pointer to the items. This is a void* so that it is
                       a generic pointer and the user avoids the urge to
                       directly index from it (you can't). */
    size_t len;     /* Number of items */
    size_t cap;     /* Number of spaces for items */
    size_t size;    /* Size of each item in bytes */
} arr;

int arr_ctor(arr *const me, const size_t cap, const size_t size);
int arr_dtor(arr *const me);

int arr_insert(arr *const me, const size_t idx, void *const item);
void *arr_search(const arr *const me, const size_t idx);
int arr_change(const arr *const me, const size_t idx, void *const restrict item, int (*item_dtor)(void *));
int arr_remove(arr *const me, const size_t idx, int (*item_dtor)(void *));
