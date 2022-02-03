#####################
try:
    import cmd
    machine.reset()
except:
    pass
#####################

from webduino import *
from machine import Pin,I2C
import time,os
from machine import Pin,I2C
import adxl345
import time

i2c = I2C(scl=Pin(4),sda=Pin(5), freq=10000)
adx = adxl345.ADXL345(i2c)
gnd = Pin(15,Pin.OUT)
gnd.off()

# wemos
wemos = Board('adxl345')
wemos.connect("KingKit_2.4G","webduino")

def runCode(ctrl):
    global sampleRate
    sampleRate=int(ctrl)

print("start...",wemos.deviceId)

#wemos.onMsg("wa5499/adxl345",runCode)
sampleRate = 50
val = 10
lastVal = 0

while True:
    x=adx.xValue
    y=adx.yValue
    z=adx.zValue
    #print('The acceleration info of x, y, z are:%d,%d,%d'%(x,y,z))
    roll,pitch = adx.RP_calculate(x,y,z)
    if(abs(roll)<15 and abs(pitch)<15):
        val = 1
    elif(abs(roll)>165 and abs(pitch)<15):
        val = 6
    elif(pitch>-90 and pitch<-70):
        val = 2
    elif(roll<0 and abs(roll)>80 and abs(pitch)<10):
        val = 3
    elif(roll>70 and abs(pitch)<10):
        val = 4
    elif(pitch>70):
        val = 5  
    if val != lastVal:
        lastVal = val
        #print('roll=',roll,',pitch=',pitch)
        print(val)
        wemos.mqtt.pub("wa5499/adxl345",str(val))
    time.sleep_ms(sampleRate)
    wemos.check()
