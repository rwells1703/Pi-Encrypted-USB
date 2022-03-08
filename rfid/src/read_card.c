#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include "pn532.h"
#include "pn532_rpi.h"

int main(int argc, char** argv) {
    uint8_t buff[255];
    uint8_t uid[MIFARE_UID_MAX_LENGTH];
    uint8_t key_a[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
    uint32_t pn532_error = PN532_ERROR_NONE;
    int32_t uid_len = 0;

    PN532 pn532;

    PN532_I2C_Init(&pn532);

    PN532_SamConfiguration(&pn532);

    do {
	// Check if a card is available to read
        uid_len = PN532_ReadPassiveTarget(&pn532, uid, PN532_MIFARE_ISO14443A, 1000);
    } while (uid_len == PN532_STATUS_ERROR);

    uint8_t block_number = 4;

    pn532_error = PN532_MifareClassicAuthenticateBlock(&pn532, uid, uid_len,
            block_number, MIFARE_CMD_AUTH_A, key_a);
    if (pn532_error != PN532_ERROR_NONE) {
        return 1;
    }
    pn532_error = PN532_MifareClassicReadBlock(&pn532, buff, block_number);
    if (pn532_error != PN532_ERROR_NONE) {
        return 1;
    }
    for (uint8_t i = 0; i < 16; i++) {
        printf("%c", buff[i]);
    }

    if (pn532_error) {
        printf("Error: 0x%02x\r\n", pn532_error);
    }
}
