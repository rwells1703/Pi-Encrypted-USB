#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include "pn532.h"
#include "pn532_rpi.h"

int main(int argc, char** argv) {
    uint8_t uid[MIFARE_UID_MAX_LENGTH];
    uint8_t key_a[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
    uint32_t pn532_error = PN532_ERROR_NONE;
    int32_t uid_len = 0;

    PN532 pn532;

    PN532_I2C_Init(&pn532);

    PN532_SamConfiguration(&pn532);

    do {
	// Check if a card is available to write
        uid_len = PN532_ReadPassiveTarget(&pn532, uid, PN532_MIFARE_ISO14443A, 1000);
    } while (uid_len == PN532_STATUS_ERROR);

    uint8_t block_number = 4;

    // Take the 64 bit data key in as text from the command line argument
    uint8_t DATA[] = {
        argv[1][0],
        argv[1][1],
        argv[1][2],
        argv[1][3],
        argv[1][4],
        argv[1][5],
        argv[1][6],
        argv[1][7],
        argv[1][8],
        argv[1][9],
        argv[1][10],
        argv[1][11],
        argv[1][12],
        argv[1][13],
        argv[1][14],
        argv[1][15]
        };

    pn532_error = PN532_MifareClassicAuthenticateBlock(&pn532, uid, uid_len,
            block_number, MIFARE_CMD_AUTH_A, key_a);

    if (pn532_error) {
        printf("Error: 0x%02x\r\n", pn532_error);
        return -1;
    }

    // Write the data to the card
    pn532_error = PN532_MifareClassicWriteBlock(&pn532, DATA, block_number);

    if (pn532_error) {
        printf("Error: 0x%02x\r\n", pn532_error);
        return -1;
    }

    printf("Write successful\r\n");
}
