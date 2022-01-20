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

def blue():
    rr.off()
    gg.off()
    bb.on()

def red():
    rr.on()
    gg.off()
    bb.off()

peer = b'\x5c\xcf\x7f\xd3\x91\xc4'
e.add_peer(peer)

gg.on()
while True:
    host, msg = e.irecv()
    if msg:
        if msg == b'red':
            red()
        if msg == b'green':
            green()
        if msg == b'blue':
            blue()
        if msg == b'end':
            break