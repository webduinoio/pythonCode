import d1motor, time
from machine import SoftI2C, Pin
from webduino import *
from machine import Pin,I2C
import time, ssd1306


def initMotor():
    global m0,m1
    i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=100000)
    m0 = d1motor.Motor(0, i2c)
    m1 = d1motor.Motor(1, i2c)    

initMotor()
m0.speed(50)
m1.speed(50)
time.sleep(1)
m0.brake()
m1.brake()

# wemos
wemos = Board()
wemos.connect("KingKit_2.4G","webduino")

def runCode(topic,msg):
    print('topic:',topic,' ,msg:',msg)
    if(topic == b'wemos/motor'):
        eval(msg.decode("utf-8"))

wemos.mqtt.sub('wemos/motor',runCode)
wemos.loop()