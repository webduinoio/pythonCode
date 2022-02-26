from webduino import *
from machine import Pin,I2C
import time,neopixel

np = neopixel.NeoPixel(machine.Pin(18), 25)

def setLED(r,g,b):    
    for led in range(25):
        np[led] = (r,g,b)
    np.write()

v2 = Board('v2')
v2.connect("KingKit_2.4G","webduino")

def runCode(topic,msg):
    topic = topic.decode("utf-8")
    msg = msg.decode("utf-8")
    print('topic:',topic,' ,msg:',msg)
    if(msg=="1"): setLED(8,1,1)
    if(msg=="2"): setLED(8,8,1)
    if(msg=="3"): setLED(8,8,8)
    if(msg=="4"): setLED(1,8,8)
    if(msg=="5"): setLED(1,8,1)
    if(msg=="6"): setLED(8,1,8)


v2.mqtt.sub('wa5499/adxl345',runCode)
# check mqtt msg
v2.loop() 



