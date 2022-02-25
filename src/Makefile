CC = gcc

SRCS = $(wildcard *.c)
all: $(SRCS:.c=.out)

PN532_LIB_PATH = ../pn532-lib
PN532_EXAMPLES_PATH = $(PN532_LIB_PATH)/examples/raspberrypi/

CFLAGS = -I$(PN532_LIB_PATH) -lwiringPi
DEPS = $(PN532_EXAMPLES_PATH)pn532.o $(PN532_EXAMPLES_PATH)pn532_rpi.o

.PHONY: clean

%.out: %.c
	$(CC) -Wall -o $@ $^ $(DEPS) $(CFLAGS)

clean:
	rm *.out