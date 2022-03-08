import machine
from machine import Pin, PWM, Timer, WDT


class LED:
    def __init__(self,pin):
        self.pin = pin
        self.led = machine.Pin(pin, machine.Pin.OUT)
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(1024)

    def on(self):
        self.pwm.duty(1023)

    def off(self):
        self.pwm.duty(0)
        
led = LED(2)
led.on()
