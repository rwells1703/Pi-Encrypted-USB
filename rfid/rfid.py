import utils

def wait_for_card():
    print("# Waiting for RFID card tap")
    stdout = utils.execute_command(["/home/pi/piusb/rfid/src/read_card.out"])
    print("# Card found")