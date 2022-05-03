#pragma once

/* This block of code must not be imported to another translation unit, lest the
typedef be defined twice. */
#ifndef __STDC_VERSION__
    typedef unsigned char Byte;
#else
    #include <inttypes.h>
    typedef uint8_t Byte;
#endif

/* Assuming that $idx * $size is a valid multiplication and that the offset
generated will create a valid address from $ptr. */
#define ARR_GETITEM(me, idx) (void *)&((Byte *)(me)->items)[(idx) * ((me)->size)]

#define SHOULD_GROW(me) ((me)->cap == (me)->len)
#define GROWTH(me) (((me)->cap > 4) ? (me)->cap * 2 : 4)
#define SHOULD_SHRINK(me) ((me)->cap / 4 >= (me)->len)
#define SHRINK(me) (((me)->cap > 4) ? (me)->cap / 2 : 4)
