from webduino import *
from machine import Pin,I2C
import time, ssd1306



# ssd1306
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)  #Init i2c
lcd = ssd1306.SSD1306_I2C(64,48,i2c) #create LCD object,Specify col and row
lcd.text("Connecting...",0,0)


wemos = Board()
wemos.connect("KingKit_2.4G","webduino")
#esp01.mqtt.pub("qq123","OKOK")
topic = {
}
def execEval(topic,msg):
    topic = topic.decode("utf-8")
    msg = msg.decode("utf-8")
    print('topic:',topic,' ,msg:',msg)
    if(topic == 'debug/display'):
        eval(msg)
        lcd.show()

wemos.mqtt.sub('debug/display',execEval)

lcd.fill(0)
lcd.text("MQTT OK!",0,0)
lcd.show()
wemos.loop()

