from webduino import *
from uyeelight import *
from machine import Pin,I2C
import time


##### Test Area #######
class Board:
    def __init__(self,readme='Unknown...'):
        self.readme = readme
        self.wifi = WiFi
        self.mqtt = MQTT
        self.wifi.onlilne(self.online)
        self.topics = {}
        self.topic_report = 'waboard/state'
        self.deviceId = self.mac().replace(':','')
        self.topic_cmd = self.deviceId+'/cmd'

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
        self.onMsg(self.topic_cmd,self.execCmd)
        self.report('boot')
        
    def onMsg(self,topic,cbFunc):
        self.topics[topic] = cbFunc
        self.mqtt.sub(topic,self.dispatch)
        
    def dispatch(self,topic,msg):
        topic = topic.decode("utf-8")
        msg = msg.decode("utf-8")
        self.topics[topic](msg)
        
    def loop(self):
        now = 0
        debug.print("run...")
        while True:
            now = now + 1
            if now % 100 == 0:
                self.mqtt.client.ping()
            self.mqtt.checkMsg()
            time.sleep(0.1)

    def check(self):
        self.mqtt.checkMsg()
        
    def ping(self):
        self.mqtt.client.ping()

    def mac(self):
        return ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    
    def report(self,cmd):
        report = cmd + ' '+self.deviceId+' '+self.readme
        self.mqtt.pub(self.topic_report,report)
    
    def execCmd(self,data):
        dataArgs = data.split(' ')
        print("exceCmd:",dataArgs)
        cmd = dataArgs[0]
        if cmd == 'reboot':
            self.report('reboot')
            time.sleep(1)
            machine.reset()
        elif cmd == 'reset':
            os.remove('main.py')
            self.report('reset')
            time.sleep(1)
            machine.reset()
        elif cmd == 'save':
            url = dataArgs[1]
            file = dataArgs[2]
            f = open('cmd.py','w')
            f.write('import os,machine\r\n')
            f.write('os.remove("cmd.py")\r\n')
            f.write('from utils import *\r\n')
            f.write('do_connect("webduino.io","webduino")\r\n')
            f.write("Utils.save('"+url+"','"+file+"')\r\n")
            f.write('machine.reset()\r\n')
            f.close()
            self.report('save')
            time.sleep(1)
            machine.reset()
##########################



# wemos
esp01 = Board('yeelight')
esp01.connect("webduino.io","webduino")
esp01.WiFi.startKeepConnect()


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

