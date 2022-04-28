import utils

def wait_for_card():
    print("# Waiting for RFID card tap")
    stdout = utils.execute_command(["/home/pi/piusb/rfid/src/read_card.out"])
    print("# Card found")

def read_card_passcode(reason):
    utils.led_on()

    print("# Waiting for RFID card containing password for " + reason)
    stdout = utils.execute_command(["/home/pi/piusb/rfid/src/read_card.out"])
    print("# Card password read")

    utils.led_off()

    # Converts passcode from bytestring to utf-8 string
    passcode = stdout.decode("utf-8")

    # Strips new line characters and null bytes from the output string
    passcode = passcode.rstrip("\r\n").rstrip("\x00")
    return passcode