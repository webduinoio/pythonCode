import network, time, machine, camera, ubinascii, os
import usocket
from machine import Pin, PWM, Timer, WDT
from umqtt.simple import MQTTClient

class debug:
    def print(msg="",msg2=""):
        #print(msg,msg2)
        pass

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
        
    def connect(ssid="ttt",pwd="webduino"):
        WiFi.ssid = ssid
        WiFi.pwd = pwd
        WiFi.sta = sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        debug.print('connecting to network...')
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
        WiFi.onlineCallback(True)
        WiFi.startKeepConnect()
        return True

    def ip():
        print(Wifi.sta.ifconfig())


class GDriver():
    def setFolderId(folderId):
        GDriver.folderId = folderId
        
    def upload(image,filename,scripId='AKfycbxc-eYgAX67kh21B9SMybSE2psXPhD5aoDDERTuFcM-IgrRBQzwvzQ6DNGPg7Ejh2ESXA'):
        url = 'https://script.google.com/macros/s/'+scripId+'/exec'
        myFilename = "filename="+str(filename)+"&folderId="+GDriver.folderId+"&data="
        data = myFilename + image.decode()
        try:
            proto, dummy, host, path = url.split("/", 3)
        except ValueError:
            proto, dummy, host = url.split("/", 2)
            path = ""
        if proto == "http:":
            port = 80
        elif proto == "https:":
            import ussl
            port = 443
        else:
            raise ValueError("Unsupported protocol: " + proto)
        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)

        ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
        ai = ai[0]
        s = usocket.socket(ai[0], ai[1], ai[2])
        s.connect(ai[-1])
        if proto == "https:":
            s = ussl.wrap_socket(s, server_hostname=host)
        s.write(b"%s /%s HTTP/1.0\r\n" % ("POST", path))
        s.write(b"Host: %s\r\n" % host)
        s.write(b"Content-Length: %d\r\n" % len(data))
        s.write(b"Content-Type: application/x-www-form-urlencoded\r\n")
        s.write(b"\r\n")
        s.write(data)
        # response
        l = s.readline()
        l = l.split(None, 2)
        status = int(l[1])
        reason = ""
        if len(l) > 2:
            reason = l[2].rstrip()
        while True:
            l = s.readline()
            if not l or l == b"\r\n":
                break
            if l.startswith(b"Transfer-Encoding:"):
                if b"chunked" in l:
                    raise ValueError("Unsupported " + l)
        return True        



class MQTT():
    
    def connect(server = 'mqtt1.webduino.io',user ='webduino' ,pwd='webduino'):
        MQTT.server = server
        MQTT.user = user
        MQTT.pwd = pwd
        MQTT.client = MQTTClient('guest', server, user=user, password=pwd)
        state = True if MQTT.client.connect() == 0 else False
        try:
            MQTT.subTopic
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

class Camera():
    def init():
        if not Camera.ready:
            try:
                camera.init(0, format=camera.JPEG,xclk_freq=camera.XCLK_20MHz)
                camera.framesize(15)
                camera.quality(10)
                camera.framesize(camera.FRAME_VGA)
                camera.framesize(camera.FRAME_UXGA)
                time.sleep(0.1)
                Camera.ready = True
            except:
                pass
    def snapshot():
        jpg = camera.capture()
        image = ubinascii.b2a_base64(jpg)
        del jpg
        time.sleep(0.1)
        gc.collect()
        return image

class WebEye():
    
    def init():
        WebEye.led = LED(4)
        WebEye.wifi = WiFi
        WebEye.mqtt = MQTT
        Camera.ready = False
        WebEye.cam = Camera
        WebEye.wifi.onlilne(WebEye.online)
        
    def online(status):
        if status:
            debug.print("online,stop blink...")
            WebEye.led.blink(1)
            WebEye.mqtt.connect()
            WebEye.led.blink(0)
        else:
            debug.print("offline,blink...")
            WebEye.led.blink(2)
            pass

    def connect(ssid='webduino.io',pwd='webduino'):
        while True:
            if WebEye.wifi.connect(ssid,pwd):
                if WebEye.mqtt.connect('mqtt1.webduino.io','webduino','webduino'):
                    break
        debug.print("WiFi Ready , MQTT Ready , ready to go...")


class CamApp():
    
    def getFilename():
        rtc = machine.RTC()
        MM = rtc.datetime()[1]
        dd = rtc.datetime()[2]
        hh = rtc.datetime()[4]
        mm = rtc.datetime()[5]
        MM = "0"+str(MM) if MM < 10 else str(MM)
        dd = "0"+str(dd) if dd < 10 else str(dd)
        hh = "0"+str(hh) if hh < 10 else str(hh)
        mm = "0"+str(mm) if mm < 10 else str(mm)
        return MM+"/"+dd+" "+hh+":"+mm

    def onMsg(topic,msg):
        print(topic+" , "+msg)
        # 重開機
        if(topic==(CamApp.name+b'/set')):
            if(msg==b'reset'):
                machine.reset()
        # 狀態查詢
        if(topic==(CamApp.name+b'/state')):
            if(msg==b'ping'):
                CamApp.eye.mqtt.pub(CamApp.name+b'/state', b'pong')
        # 補光燈
        if(topic==(CamApp.name+b'/led')):
            try:
                CamApp.eye.led.on(int(msg))
            except:
                CamApp.eye.led.on(1000)
        # 拍照
        if(topic==(CamApp.name+b'/snapshot')):
            if(msg==b'now'):
                CamApp.eye.mqtt.pub((CamApp.name+b'/state'), b'waiting')
                image = CamApp.eye.cam.snapshot()
                CamApp.eye.mqtt.pub((CamApp.name+b'/state'), b'upload')
                GDriver.upload(CamApp.eye.cam.snapshot(),"set-"+CamApp.getFilename())
                CamApp.eye.mqtt.pub((CamApp.name+b'/state'), b'upload ok')

    def init(name,ssid,pwd):
        CamApp.wdt = WDT(timeout=30000)
        print("init CamApp...")
        CamApp.eye = WebEye
        CamApp.eye.init()
        print("connect...")
        CamApp.eye.connect(ssid,pwd)
        CamApp.eye.cam.init()
        CamApp.name = str.encode(name)
        CamApp.eye.mqtt.sub(CamApp.name+b'/#',CamApp.onMsg)
        CamApp.eye.mqtt.pub((CamApp.name+b'/state'), b'Ready')
        print("ready to go...")

    def run():
        now = 0
        min = 10*60*10 # 10 min
        while True:
            CamApp.wdt.feed()
            now = now + 1
            if now == min:
                now = 0
                CamApp.eye.mqtt.pub((CamApp.name+b'/state'), b'waiting')
                image = CamApp.eye.cam.snapshot()
                CamApp.eye.mqtt.pub((CamApp.name+b'/state'), b'upload')
                GDriver.upload(CamApp.eye.cam.snapshot(),CamApp.getFilename())
                CamApp.eye.mqtt.pub((CamApp.name+b'/state'), b'upload ok')        
            CamApp.eye.mqtt.checkMsg()
            time.sleep(0.1)

# eye01 folder's
GDriver.setFolderId('1DrhYTKccer3SSrxSzRxh2fQ-7CZBU01Z')
CamApp.init('eye01','KingKit_2.4G','webduino')

# wa001 folder's 
#GDriver.setFolderId('1oaJx5OUOK8FekcANGgr972thFjm-AFrv')
#CamApp.init('wa001','KingKit_2.4G','webduino')

CamApp.run()