import machine
import time
ledD2 = machine.Pin(1, machine.Pin.OUT)
for i in range(10):
    print("off")
    ledD2.off()
    time.sleep(0.5)
    print("on")
    ledD2.on()
    time.sleep(0.5)
    