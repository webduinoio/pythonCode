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

btn315_blue   = "659aaaaa5959"
btn315_red    = "6559a6996959"
btn315_yellow = "556a6555a959"
# wemos
wemos = Board('App')
wemos.connect("KingKit_2.4G","webduino")
def runCode(code):
    print("btnCode:",code)
    if code == btn315_red:
        wemos.mqtt.pub("wa5499/bulb","bulb.set_rgb(255,2,2,duration=1)")
    if code == btn315_blue:
        wemos.mqtt.pub("wa5499/bulb","bulb.set_rgb(2,2,255,duration=1)")
    if code == btn315_yellow:
        wemos.mqtt.pub("wa5499/bulb","bulb.set_rgb(255,255,2,duration=1)")

print("start...",wemos.deviceId)
wemos.onMsg('wa5499/btn',runCode)
wemos.loop()
"""    
btn1 = "5556565a5556"
btn2 = "5566959a5556"
btn3 = "5559565a5556"
btn4 = "555aa5aa5556"
"""
