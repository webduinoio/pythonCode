import network
from esp import espnow
import machine, neopixel,time,random

np = neopixel.NeoPixel(machine.Pin(4), 25)
w0 = network.WLAN(network.STA_IF)

def setLED(r,g,b):    
    for led in range(25):
        np[led] = (r,g,b)
    np.write()

setLED(3,0,0)

w0.active(True)
e = espnow.ESPNow()
e.init()
setLED(3,3,0)
peer = b'\x5c\xcf\x7f\x81\xa2\xd7'
e.add_peer(peer) 

setLED(0,0,3)
for i in range(10000):
    setLED(0,3,0)
    e.send(peer, b'ring', False)
    time.sleep(0.5)
    setLED(3,0,0)
    time.sleep(0.5)
