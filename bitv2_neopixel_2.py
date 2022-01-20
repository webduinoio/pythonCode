import machine, neopixel,time,random

strong = 10
n = 25
p = 18
np = neopixel.NeoPixel(machine.Pin(p), n)

def clear():    
    for led in range(25):
        np[led] = (0,0,0)
    np.write()

def show():
    for t in range(10000):
        led = random.randint(0,24)
        r = random.randint(0,strong)
        g = random.randint(0,strong)
        b = random.randint(0,strong)
        np[led] = (r,g,b)
        np.write()
        time.sleep(0.001)
show()
clear()