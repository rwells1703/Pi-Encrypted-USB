import utils

def wait_for_card():
    print("# Waiting for RFID card tap")
    stdout = utils.execute_command(["./rfid/src/read_card.out"])
    print("# Card found")

def read_card_passcode(reason):
    print("# Waiting for RFID card passcode for " + reason)
    stdout = utils.execute_command(["./rfid/src/read_card.out"])
    print("# Card passcode read")

    # Converts passcode from bytestring to utf-8 string
    passcode = stdout.decode("utf-8")

    # Strips new line characters and null bytes from the output string
    passcode = passcode.rstrip("\r\n").rstrip("\x00")

    return passcode