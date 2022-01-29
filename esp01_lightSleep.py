import time,esp
from machine import Pin
print("goto sleep...")
pin = Pin(1, Pin.OUT)

def flash():
    for i in range(3):
        pin.off()
        time.sleep(0.5)
        pin.on()
        time.sleep(0.5)

flash()
machine.lightsleep(30*1000)
pin.on()
print("wakeup!")
flash()

