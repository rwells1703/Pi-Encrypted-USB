import subprocess
import time

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