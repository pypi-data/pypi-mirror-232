
#ifdef __IDE_ONLY__
#include "clynton/prelude.h"
#endif

void Clynton_PreserveHeap(void *dest, ...) {
    va_list(ap);
    va_start(ap, dest);

    char *w = (char *)dest;

    for (;;) {
        void *source = va_arg(ap, void *);
        if (source == NULL) {
            break;
        }

        size_t size = va_arg(ap, size_t);
        memcpy(w, source, size);
        w += size;
    }
}

void Clynton_RestoreHeap(void *source, ...) {
    va_list(ap);
    va_start(ap, source);

    char *w = (char *)source;

    for (;;) {
        void *dest = va_arg(ap, void *);
        if (dest == NULL) {
            break;
        }

        size_t size = va_arg(ap, size_t);
        memcpy(dest, w, size);
        w += size;
    }
}
