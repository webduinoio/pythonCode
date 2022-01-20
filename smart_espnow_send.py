import network,machine,time
from machine import Pin,PWM
from esp import espnow

gg=machine.Pin(12, machine.Pin.OUT) 
bb=machine.Pin(13, machine.Pin.OUT) 
rr=machine.Pin(15, machine.Pin.OUT) 

w0 = network.WLAN(network.STA_IF)
w0.active(True)
e = espnow.ESPNow()
e.init()

def off():
    rr.off()
    gg.off()
    bb.off()

def green():
    rr.off()
    gg.on()
    bb.off()
    e.send(peer, b'green', True)

def blue():
    rr.off()
    gg.off()
    bb.on()
    e.send(peer, b'blue', True)

def red():
    rr.on()
    gg.off()
    bb.off()
    e.send(peer, b'red', True)

peer = b'\x5c\xcf\x7f\x28\xc4\xee'
e.add_peer(peer)

btn=Pin(4, Pin.IN, Pin.PULL_UP)
switch = {0 : green, 1: red, 2:blue}
idx = 0
print("start...")
while True:
    if btn.value() == 0:
        idx = (idx + 1) % 3
        switch[idx]()
        time.sleep(0.5)