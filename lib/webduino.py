import network, time, machine, ubinascii, os
import usocket
from machine import Pin, PWM, Timer, WDT
from umqtt.simple import MQTTClient

class debug:
    state = True
    def on():
        debug.state = True
    def off():
        debug.state = False
    def print(msg="",msg2="",msg3=""):
        if debug.state:
            print(msg,msg2)

class LED():
    def __init__(self,pin,pwm=True):
        self.pin = pin
        self.strong=2
        self.state = False
        self.timer = None
        self.isBlink = False
        if pwm:
            self.pwm = PWM(Pin(pin))
            self.pwm.freq(1024)
            self.pwm.duty(0)
        self.off()
        time.sleep(0.01)
        self.off()
        time.sleep(0.01)
        self.off()
        time.sleep(0.01)
            
    def on(self,strong=-1):
        self.state = True
        if not strong == -1:
            self.strong= strong
        self.pwm.duty(self.strong)
        
    def off(self):
        self.state = False
        self.pwm.duty(0)
    
    def run(self,n):
        if self.isBlink:
            if self.state:
                self.off()
            else:
                self.on()
    
    def blink(self,peroid):
        _p_ = int(peroid*1000)
        if _p_ == 0:
            self.isBlink = False
            self.off()
            return
        else:
            self.isBlink = True
            self.on()
        
        if self.timer == None:
            self.timer = Timer(1)
            self.timer.init(period=_p_, mode=Timer.PERIODIC, callback=self.run)
            debug.print("LED:default use Timer(0)",self.timer)
        else:
            self.timer.deinit()
            self.timer = Timer(1)
            self.timer.init(period=_p_, mode=Timer.PERIODIC, callback=self.run)
            
class WiFi:
    onlineCallback = None
    def disconnect():
        WiFi.sta.disconnect()

    def check():
        print(WiFi.sta.isconnected())

    def onlilne(cb):
        WiFi.onlineCallback = cb

    def startKeepConnect():
        WiFi.timer = Timer(0)
        WiFi.timer.init(period=3000, mode=Timer.PERIODIC, callback=WiFi.checkConnection)
        
    def checkConnection(t):
        #print("wifi:",WiFi.sta.isconnected())
        if not WiFi.sta.isconnected():
            debug.print("connect broke ! retry...")
            WiFi.connect(WiFi.ssid,WiFi.pwd)
            debug.print("!!!! online callback... !!!!")
        
    def connect(ssid="webduino.io",pwd="webduino"):
        WiFi.ssid = ssid
        WiFi.pwd = pwd
        WiFi.sta = sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        debug.print('connecting to network...')
        if(WiFi.onlineCallback is not None):
            WiFi.onlineCallback(False)
        if not sta_if.isconnected():
            try:
                sta_if.connect(ssid,pwd)
            except:
                debug.print("connect...")
        cnt = 0
        while not sta_if.isconnected():
            cnt = cnt + 1
            time.sleep(0.5)
            if cnt == 10:
                cnt = 0
                debug.print("retry connect...")
        WiFi.ip = WiFi.sta.ifconfig()[0];
        if(WiFi.onlineCallback is not None):
            WiFi.onlineCallback(True)
        WiFi.startKeepConnect()
        return True

    def ip():
        return WiFi.sta.ifconfig()

class MQTT():
    
    def connect(server = 'mqtt1.webduino.io',user ='webduino' ,pwd='webduino'):
        MQTT.server = server
        MQTT.user = user
        MQTT.pwd = pwd
        mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode().replace(':','')
        MQTT.client = MQTTClient('wa'+mac, server, user=user, password=pwd)
        state = True if MQTT.client.connect() == 0 else False
        try:
            debug.print("resubscribe:",MQTT.subTopic)
            MQTT.sub(MQTT.subTopic,MQTT.callback)
        except:
            pass
        return state
        
    def pub(topic,msg):
        MQTT.client.publish(topic,msg)

    def sub(topic,cb):
        MQTT.subTopic = topic
        MQTT.callback = cb
        MQTT.client.set_callback(cb)
        MQTT.client.subscribe(topic)

    def checkMsg():
        try:
            MQTT.client.check_msg()
        except:
            pass


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