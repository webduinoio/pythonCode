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
from utils import *
import time



def beep(t=1):
    beep = Pin(12,Pin.OUT)
    for i in range(t):
        beep.off()
        time.sleep(0.05)
        beep.on()
        time.sleep(0.05)
        
class Board:
    def __init__(self,readme='Unknown...'):
        self.readme = readme
        self.wifi = WiFi
        self.mqtt = MQTT
        self.wifi.onlilne(self.online)
        self.topics = {}
        self.topic_report = 'waboard/state'
        self.deviceId = self.mac().replace(':','')
        self.deviceId = 'gogogo'
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
        debug.print("run...")
        now = 0
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
        if cmd == 'reset':
            machine.reset()
        elif cmd == 'save':
            f = open('cmd.py','w')
            f.write('import os,machine\r\n')
            f.write('os.remove("cmd.py")\r\n')
            f.write('from utils import *\r\n')
            f.write('do_connect("webduino.io","webduino")\r\n')
            f.write("Utils.save('https://share.webduino.io/storage/download/0131_001907.211_main.py','main.py')\r\n")
            f.write('machine.reset()\r\n')
            f.close()
            self.report('save')
            machine.reset()

# wemos
wemos = Board('RF318Mhz')
wemos.connect("KingKit_2.4G","webduino")

def runCode(msg):
    beep(3)

publishTopic = "gateway/btn"
print("start...",wemos.deviceId)

wemos.onMsg(publishTopic,runCode)
pin5 = Pin(5,Pin.IN)
    
btn1 = "5556565a5556"
btn2 = "5566959a5556"
btn3 = "5559565a5556"
btn4 = "555aa5aa5556"
btn315_blue   = "659aaaaa5959"
btn315_red    = "6559a6996959"
btn315_yellow = "556a6555a959"

while True:
    data = RFBtn.listener(pin5,wemos.check)
    if(len(data)==12):
        beep(1)
        wemos.mqtt.pub(publishTopic,data)