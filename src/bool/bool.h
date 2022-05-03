#pragma once

#ifndef __STDC_VERSION__    /* C89 */
typedef enum {
    false = 0, true = 1
} bool;
#else
#include <stdbool.h>
#endif