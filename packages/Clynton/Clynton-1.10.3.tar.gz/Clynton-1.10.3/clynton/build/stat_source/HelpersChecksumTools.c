
#ifdef __IDE_ONLY__
#include "clynton/prelude.h"
#endif

uint32_t initCRC32(void) { return 0xFFFFFFFF; }

uint32_t updateCRC32(uint32_t crc, unsigned char const *message, uint32_t size) {
    for (uint32_t i = 0; i < size; i++) {
        unsigned int c = message[i];
        crc = crc ^ c;

        for (int j = 7; j >= 0; j--) {
            uint32_t mask = ((crc & 1) != 0) ? 0xFFFFFFFF : 0;
            crc = (crc >> 1) ^ (0xEDB88320 & mask);
        }
    }

    return crc;
}

uint32_t finalizeCRC32(uint32_t crc) { return ~crc; }

// No Python runtime is available yet, need to do this in C.
uint32_t calcCRC32(unsigned char const *message, uint32_t size) {
    return finalizeCRC32(updateCRC32(initCRC32(), message, size));
}
