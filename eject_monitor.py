#!/usr/bin/python3

import time
import subprocess
import select

f = subprocess.Popen(['tail','-F','/var/log/syslog'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
p = select.poll()
p.register(f.stdout)

while True:
    if p.poll(1):
        if f.stdout.readline().decode("utf-8").strip().endswith("USB DEVICE HAS BEEN EJECTED"):
            subprocess.Popen(['sudo','poweroff'])
    time.sleep(0.001)
