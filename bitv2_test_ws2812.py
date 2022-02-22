from webduino import Board
import network
import machine, neopixel,time,random
import esp
#esp.osdebug(0,esp.LOG_INFO)
bb = 5
machine.freq(240000000)

def setLED(r,g,b):    
    for led in range(25):
        np[12] = (r,g,b)
        #state = machine.disable_irq()
        np.write()
        #machine.enable_irq(state)

def pureStart():
    for i in range(1000):
        led = i % 6
        if led == 0:
            setLED(bb,0,0)
        if led == 1:
            setLED(bb,bb,0)
        if led == 2:
            setLED(0,bb,bb)
        if led == 3:
            setLED(bb,0,bb)
        if led == 4:
            setLED(bb,bb,bb)
        if led == 5:
            setLED(0,0,0)


def ctrlLED(cmd):
    print("cmd:",cmd)
    data = cmd.split(' ')
    led = int(data[1]) % 6
    if led == 0:
        setLED(bb,0,0)
    if led == 1:
        setLED(bb,bb,0)
    if led == 2:
        setLED(0,bb,bb)
    if led == 3:
        setLED(bb,0,bb)
    if led == 4:
        setLED(bb,bb,bb)
    if led == 5:
        setLED(0,0,0)
    #eval(cmd)

def boardStart():
    bit = Board(devId='home',enableAP=False)
    bit.connect('webduino.io','webduino')
    setLED(0,5,0)
    print("start...")
    bit.onMsg('ledTest',ctrlLED)
    bit.loop()

print(1)
np = neopixel.NeoPixel(machine.Pin(18), 25)
print(2)
setLED(5,0,0)
print(3)
boardStart()
#pureStart()