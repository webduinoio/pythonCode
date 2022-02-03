from webduino import *
from uyeelight import *
from machine import Pin,I2C
import time


##### Test Area #######

##########################

# wemos
esp01 = Board('yeelight')
esp01.connect("webduino.io3","webduino")


def ctrlBulb(cmd):
    print("cmd:",cmd)
    eval(cmd)

publishTopic = "wa5499/bulb"
print("start...",esp01.deviceId)

esp01.onMsg(publishTopic,ctrlBulb)
"""
bulbs = Bulb.search(timeout=5,debug=True)

if len(bulbs)==0:
    raise Exception("bulb not found.")

ip = list(bulbs.keys())[0]
bulb = Bulb(ip)
"""
bulb = Bulb("192.168.0.95")
bulb.turn_on()
bulb.set_rgb(255,2,2,duration=1)
esp01.loop()

