
#ifdef __IDE_ONLY__
#if defined(_WIN32)
#include <windows.h>
#endif
#include <stdbool.h>
#endif

#include "clynton/safe_string_ops.h"

void copyStringSafe(char *buffer, char const *source, size_t buffer_size) {
    if (strlen(source) >= buffer_size) {
        abort();
    }

    if (buffer != source) {
        strcpy(buffer, source);
    }
}

void copyStringSafeN(char *buffer, char const *source, size_t n, size_t buffer_size) {
    if (n >= buffer_size - 1) {
        abort();
    }
    strncpy(buffer, source, n);
    buffer[n] = 0;
}

void copyStringSafeW(wchar_t *buffer, wchar_t const *source, size_t buffer_size) {
    while (*source != 0) {
        if (buffer_size < 1) {
            abort();
        }

        *buffer++ = *source++;
        buffer_size -= 1;
    }

    *buffer = 0;
}

void appendStringSafe(char *target, char const *source, size_t buffer_size) {
    if (strlen(source) + strlen(target) >= buffer_size) {
        abort();
    }
    strcat(target, source);
}

void appendCharSafe(char *target, char c, size_t buffer_size) {
    char source[2] = {c, 0};

    appendStringSafe(target, source, buffer_size);
}

void appendWStringSafeW(wchar_t *target, wchar_t const *source, size_t buffer_size) {
    while (*target != 0) {
        target++;
        buffer_size -= 1;
    }

    while (*source != 0) {
        if (buffer_size < 1) {
            abort();
        }

        *target++ = *source++;
        buffer_size -= 1;
    }

    *target = 0;
}

void appendCharSafeW(wchar_t *target, char c, size_t buffer_size) {
    while (*target != 0) {
        target++;
        buffer_size -= 1;
    }

    if (buffer_size < 1) {
        abort();
    }

    target += wcslen(target);
    char buffer_c[2] = {c, 0};
    size_t res = mbstowcs(target, buffer_c, 2);
    assert(res == 1);
}

void appendStringSafeW(wchar_t *target, char const *source, size_t buffer_size) {
    while (*target != 0) {
        target++;
        buffer_size -= 1;
    }

    while (*source != 0) {
        appendCharSafeW(target, *source, buffer_size);
        source++;
        buffer_size -= 1;
    }
}

void printOSErrorMessage(char const *message, error_code_t error_code) {
#if defined(_WIN32)
    LPCTSTR err_buffer;

    FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS, NULL,
                  error_code, MAKELANGID(LANG_ENGLISH, SUBLANG_ENGLISH_US), (LPTSTR)&err_buffer, 0, NULL);

    fprintf(stderr, "%s ([Error %d] %s)\n", message, error_code, err_buffer);
#else
    fprintf(stderr, "%s: %s\n", message, strerror(error_code));
#endif
}
