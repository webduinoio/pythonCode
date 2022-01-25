from webduino import *
from machine import Pin,I2C
import time

# esp01
esp01 = Board()
esp01.connect("KingKit_2.4G","webduino")
esp01.mqtt.pub("qq123","OKOK")

def onMsg(topic,msg):
    print(topic,msg)

esp01.mqtt.sub('debug/display',onMsg)
esp01.loop()
