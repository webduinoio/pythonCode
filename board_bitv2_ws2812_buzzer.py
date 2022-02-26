from machine import ADC, I2C, Pin
import os,machine,math,neopixel,time,random

np = neopixel.NeoPixel(machine.Pin(18), 25)

def setLED(r,g,b):    
    for led in range(25):
        np[led] = (r,g,b)
    np.write()
    
class Buzzer():
    # 262 294 330 349 392 440 494
    def play(self,freq=300,delay=0.1):
        pin17 = machine.PWM(machine.Pin(17), duty=512)
        pin17.freq(freq)
        time.sleep(delay)
        machine.PWM(machine.Pin(17), duty=0)

p0 = ADC(Pin(3))
p0.atten(ADC.ATTN_0DB)

p1 = ADC(Pin(1))
p1.atten(ADC.ATTN_0DB)

p2 = ADC(Pin(2))
p2.atten(ADC.ATTN_0DB)

buzzer = Buzzer()


while True:
    if(p0.read()<20):
        print("Do "+str(p0.read()))
        buzzer.play(262,0.1)
        setLED(5,0,0)
        time.sleep(0.1)
    if(p1.read()<20):
        print("Re "+str(p1.read()))
        buzzer.play(349,0.1)
        setLED(0,5,0)        
        time.sleep(0.1)
    if(p2.read()<20):
        print("Me "+str(p2.read()))
        buzzer.play(494,0.1)
        setLED(0,0,5)
        time.sleep(0.1)