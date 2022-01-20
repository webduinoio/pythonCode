import network
from esp import espnow
from machine import Pin,PWM
import time

def ringTone(n):
    pwm = PWM(Pin(0))
    Pin(2).off()
    for i in range(0,n):
        pwm.init(1000,512)
        time.sleep_ms(50)
        pwm.freq(500)
        time.sleep_ms(50)
        pwm.deinit()

def initESPNow():
    w0 = network.WLAN(network.STA_IF)
    w0.active(True)
    e = espnow.ESPNow()
    e.init()
    peer = b'\x30\xae\xa4\xef\xe9\x3c'
    e.add_peer(peer)
    return e

e = initESPNow()
ringTone(1)
print("gogogo...")

while True:
    print("...")
    host, msg = e.irecv(3000)
    print(host,msg)
    if msg:
        if msg == b'ring':
            ringTone(10)
        if msg == b'end':
            break

