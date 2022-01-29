from webduino import *
from machine import Pin,I2C
import time, webrepl, dht, machine, _thread



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
                self.mqtt.client.ping()
            self.mqtt.checkMsg()
            time.sleep(0.1)


# esp01
esp01 = Board()
esp01.init()
esp01.connect("KingKit_2.4G","webduino")
d = dht.DHT22(machine.Pin(2))

def read():
    print('d.measure():',d.measure())
    print('d.temperature():',d.temperature())
    print('d.humidity():',d.humidity())



def runCode(topic,msg):
    topic = topic.decode("utf-8")
    msg = msg.decode("utf-8")
    print('topic:',topic,' ,msg:',msg)
    if(topic == 'debug/exec'):
        eval(msg)

esp01.mqtt.sub('debug/exec',runCode)
_thread.start_new_thread(esp01.loop, ())
webrepl.start()