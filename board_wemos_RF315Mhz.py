#####################
try:
    import cmd
    machine.reset()
except:
    pass
#####################

from webduino import *
from machine import Pin,I2C
from utime import ticks_us, ticks_diff
from array import array
from RFBtn import RFBtn
import time,os
 
def beep(t=1):
    beep = Pin(12,Pin.OUT)
    for i in range(t):
        beep.off()
        time.sleep(0.05)
        beep.on()
        time.sleep(0.05)

# wemos
wemos = Board('RF318Mhz')
wemos.connect("KingKit_2.4G","webduino")

def runCode(msg):
    beep(3)

publishTopic = "gateway/btn"
print("start...",wemos.deviceId)

wemos.onMsg(publishTopic,runCode)
pin5 = Pin(5,Pin.IN)
    
btn1 = "5556565a5556"
btn2 = "5566959a5556"
btn3 = "5559565a5556"
btn4 = "555aa5aa5556"
btn315_blue   = "659aaaaa5959"
btn315_red    = "6559a6996959"
btn315_yellow = "556a6555a959"
beep(5)

while True:
    data = RFBtn.listener(pin5,wemos.check)
    if(len(data)==12):
        beep(1)
        wemos.mqtt.pub(publishTopic,data)

