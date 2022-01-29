from machine import Pin
from rfsocket import RFSocket
import time

p = Pin(1,Pin.OUT)
r = RFSocket(p)
toggle = True
while True:
    if toggle:
        r.group_on()
        p.on()
    else:
        r.group_off()
        p.off()
    toggle = not toggle
    time.sleep(1)
