#pragma once

int mem_new(void **const p, const size_t size);
int mem_del(void **const p);
int mem_resize(void **const p, const size_t size);