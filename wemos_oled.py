from webduino import *
from machine import Pin,I2C
import time, ssd1306

# ssd1306
i2c = I2C(scl=Pin(0), sda=Pin(2), freq=100000)  #Init i2c
lcd = ssd1306.SSD1306_I2C(128,64,i2c) #create LCD object,Specify col and row


class Board:
    
    def init(self):
        self.wifi = WiFi
        self.mqtt = MQTT
        self.wifi.onlilne(self.online)
        
    def online(self,status):
        if status:
            debug.print("connect mqtt...")
            self.mqtt.connect()
            debug.print("mqtt OK")
            lcd.text("MQTT connnected!",0,0)
            lcd.show()
        else:
            debug.print("offline...")
            pass

    def connect(self,ssid='webduino.io',pwd='webduino'):
        while True:
            if self.wifi.connect(ssid,pwd):
                if self.mqtt.connect('mqtt1.webduino.io','webduino','webduino'):
                    break
        debug.print("WiFi Ready , MQTT Ready , ready to go...")
    
    def loop(self):
        debug.print("run...")
        now = 0
        while True:
            now = now + 1
            if now % 100 == 0:
                CamApp.eye.mqtt.client.ping()
            self.mqtt.checkMsg()
            time.sleep(0.1)


# wemos
wemos = Board()
wemos.init()
wemos.connect("KingKit_2.4G","webduino")

def execEval(topic,msg):
    topic = topic.decode("utf-8")
    msg = msg.decode("utf-8")
    print('topic:',topic,' ,msg:',msg)
    if(topic == 'display'):
        eval(msg)
        lcd.show()

esp01.mqtt.sub('debug/display',execEval)
esp01.loop()