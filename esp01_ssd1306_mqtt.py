from webduino import *
from machine import Pin,I2C
import time, ssd1306

# ssd1306
i2c = I2C(scl=Pin(0), sda=Pin(2), freq=100000)  #Init i2c
lcd = ssd1306.SSD1306_I2C(128,64,i2c) #create LCD object,Specify col and row

# esp01
esp01 = Board()
esp01.init()
esp01.connect("KingKit_2.4G","webduino")
#esp01.mqtt.pub("qq123","OKOK")

def execEval(topic,msg):
    topic = topic.decode("utf-8")
    msg = msg.decode("utf-8")
    print('topic:',topic,' ,msg:',msg)
    if(topic == 'debug/display'):
        eval(msg)
        lcd.show()

esp01.mqtt.sub('debug/display',execEval)

lcd.fill(0)
lcd.text("MQTT connnected!",0,0)
lcd.show()
esp01.loop()