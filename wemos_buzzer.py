from machine import Pin , PWM
import utime

al = Pin(1,Pin.IN,Pin.PULL_UP)

while True:
    if al.value()==1:
        beeper = PWM(Pin(14, Pin.OUT),freq=440, duty=512)
        utime.sleep(1)
        beeper.deinit()
