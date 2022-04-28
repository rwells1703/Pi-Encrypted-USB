import subprocess

import encryption

debug = False

def execute_command(command):
    process = subprocess.Popen(command, env=encryption.get_tpm_shell_env() ,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()

    if debug:
        print(stdout.decode("utf-8"))

    return stdout

def disable_led_trigger():
    subprocess.run("sh -c \"echo none > /sys/class/leds/led0/trigger\"", shell=True)

def led_on():
    subprocess.run("sh -c \"echo 1 > /sys/class/leds/led0/brightness\"", shell=True)

def led_off():
    subprocess.run("sh -c \"echo 0 > /sys/class/leds/led0/brightness\"", shell=True)

def led_flicker():
    led_on()
    led_off()