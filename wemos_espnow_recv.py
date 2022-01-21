import network
from esp import espnow
import machine, neopixel

w0 = network.WLAN(network.STA_IF)
np = neopixel.NeoPixel(machine.Pin(4), 1)

def setLED(r,g,b):    
    np[0] = (r,g,b)
    np.write()

setLED(3,0,0)
w0.active(True)
e = espnow.ESPNow()
e.init()

setLED(3,3,0)
peer = b'\xe8\xdb\x84\xae\x2b\x2b'
e.add_peer(peer)

setLED(0,3,0)
while True:
    host, msg = e.irecv()
    if msg:
        if msg == b'red':
            setLED(3,0,0)
        if msg == b'green':
            setLED(0,3,0)
        if msg == b'blue':
            setLED(0,0,3)
        if msg == b'end':
            break