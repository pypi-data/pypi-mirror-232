
#ifdef __IDE_ONLY__
#include "clynton/prelude.h"
#endif

#include <float.h>

/* Check if unary negation would not fit into long */
#define UNARY_NEG_WOULD_OVERFLOW(x) ((x) < 0 && (unsigned long)(x) == 0 - (unsigned long)(x))
/* This is from pyport.h */
#define WIDTH_OF_ULONG (CHAR_BIT * SIZEOF_LONG)
