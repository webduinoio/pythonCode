import network
from esp import espnow
import machine, neopixel,time,random

w0 = network.WLAN(network.STA_IF)
np = neopixel.NeoPixel(machine.Pin(4), 1)

def setLED(r,g,b):    
    np[0] = (r,g,b)
    np.write()

w0.active(True)
e = espnow.ESPNow()
e.init()
setLED(3,3,0)
#peer = b'\x30\xae\xa4\xf6\xf2\x98' # sender's mac
peer = b'\x18\xfe\x34\xcc\x45\x30' # receiver/s mac
e.add_peer(peer) 

setLED(0,0,3)
for i in range(10000):
    e.send(peer, b'red', False)
    setLED(3,0,0)
    time.sleep(0.5)
    e.send(peer, b'green', False)
    setLED(0,3,0) 
    time.sleep(0.5)
    e.send(peer, b'blue', False)
    setLED(0,0,3)
    time.sleep(0.5)
