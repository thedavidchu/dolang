/* A file containing the compatibility differences between compilers. */

#pragma once

/* Allow use of inline in this file, even if it is not valid. */
#ifndef __STDC_VERSION__
/* NOTE: the user should not use either of these words */
#   define inline
#   define restrict
#endif