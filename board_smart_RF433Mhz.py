#####################
try:
    import cmd
    machine.reset()
except:
    pass
#####################

# mac Address: 5c:cf:7f:81:0f:b5
from webduino import *
from machine import Pin,I2C
from utime import ticks_us, ticks_diff
from array import array
from RFBtn import RFBtn
import time,os

gnd = Pin(16,Pin.OUT)
gnd.on()

def beep(t=1):
    beep = Pin(14,Pin.OUT)
    for i in range(t):
        beep.off()
        time.sleep(0.015)
        beep.on()
        time.sleep(0.005)

beep(2)

# wemos
wemos = Board('RF433Mhz')
wemos.connect("KingKit_2.4G","webduino")

# btn
btn1 = "5556565a5556"
btn2 = "5566959a5556"
btn3 = "5559565a5556"
btn4 = "555aa5aa5556"
btn315_blue   = "659aaaaa5959"
btn315_red    = "6559a6996959"
btn315_yellow = "556a6555a959"

def runCode(code):
    if code == btn1 or code == btn2 or code == btn3 or code == btn4:
        beep(1)

publishTopic = "wa5499/btn433"
print("start...",wemos.deviceId)
wemos.onMsg(publishTopic,runCode)
pin5 = Pin(5,Pin.IN)

beep(1)
while True:
    data = RFBtn.listener(pin5,wemos.check)
    print(data)
    if(len(data)==12):
        wemos.mqtt.pub(publishTopic,data)
