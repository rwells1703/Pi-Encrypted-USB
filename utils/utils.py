import subprocess
import time

import encryption

# Enable more detailed logging of command output/errors
DEBUG = False

# Spawns a subprocess for the given shell command, and logs its output
def execute_command(command):
    process = subprocess.Popen(command, env=encryption.get_tpm_shell_env() ,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()

    log(stdout.decode("utf-8"))

    return stdout

# Log a message to the console if debug is enabled
def log(message):
    if DEBUG:
        print(message)

# Changes default behaviour of onboard Raspberry Pi LED from CPU load to a custom use
def disable_led_trigger():
    subprocess.run("sh -c \"echo none > /sys/class/leds/led0/trigger\"", shell=True)

# Turn on the onboard LED
def led_on():
    subprocess.run("sh -c \"echo 1 > /sys/class/leds/led0/brightness\"", shell=True)

# Turn off the onboard LED
def led_off():
    subprocess.run("sh -c \"echo 0 > /sys/class/leds/led0/brightness\"", shell=True)

# Quickly flicker the onboard LED
def led_flicker(duration):
    led_on()
    time.sleep(duration)
    led_off()