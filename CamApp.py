import network, time, machine, camera, ubinascii, os
import usocket, ntptime, random
from machine import Pin, PWM, Timer, WDT
from umqtt.simple import MQTTClient

class debug:
    def print(msg="",msg2="",msg3=""):
        print("[debug]",msg,msg2,msg3)
        pass

class GDriver:
    def setFolderId(folderId):
        GDriver.folderId = folderId
        
    def upload(image,filename,scripId='AKfycbxtT6V-ndoqFYvgz-rjK7fDYTAP8TcMuOl_CVSgwSYve3arbeXWfHBn_bjLADG4eXcTCQ'):
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
            #print("resp:",l)
            if not l or l == b"\r\n\r\n":
                break
            if l.startswith(b"Transfer-Encoding:"):
                if b"chunked" in l:
                    raise ValueError("Unsupported " + l)
        return True        

class LED:
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
   
class Camera():
    
    def init():
        try:
            Camera.initState
        except:
            Camera.initState = 0
        if Camera.initState is not 1:
            try:
                camera.init(0, format=camera.JPEG,xclk_freq=camera.XCLK_20MHz)
                camera.framesize(15)
                camera.quality(10)
                #camera.framesize(camera.FRAME_VGA)
                camera.framesize(camera.FRAME_UXGA)
                time.sleep(0.1)
                Camera.initState = 1
            except:
                print("Camera exception !!!")
                Camera.initState = -1
                machine.reset()
                pass
            
    def snapshot():
        jpg = camera.capture()
        image = ubinascii.b2a_base64(jpg)
        del jpg
        time.sleep(0.1)
        gc.collect()
        return image


class WiFi:

    def ip():
        print(Wifi.sta.ifconfig())
        
    def check():
        print(WiFi.sta.isconnected())

    def disconnect():
        WiFi.sta.disconnect()

    def checkConnection():
        debug.print("wifi state:",WiFi.sta.isconnected())
        if not WiFi.sta.isconnected():
            debug.print("connect broke ! retry...")
            WiFi.connect()
            debug.print("!!!! online callback... !!!!")

    def setup(ssid="webduino.io",pwd="webduino"):
        WiFi.ssid = ssid
        WiFi.pwd = pwd

    def connect():
        WiFi.sta = sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        debug.print('connecting WiFi:',WiFi.ssid,WiFi.pwd)
        cnt = 0
        sta_if.connect(WiFi.ssid,WiFi.pwd)
        while not sta_if.isconnected():
            cnt = cnt + 1
            time.sleep(0.5)
            if cnt == 10:
                cnt = 0
                debug.print("retry connect...")
        WiFi.ip = sta_if.ifconfig()[0];
        return True

class MQTT():
    def setup(server = 'mqtt1.webduino.io',user ='webduino' ,pwd='webduino',keepalive=60):
        MQTT.user = user
        MQTT.pwd = pwd
        MQTT.server = server
        userId = 'guest'+str(random.randint(0,10000))
        MQTT.client = MQTTClient(userId, MQTT.server, user=MQTT.user, password=MQTT.pwd)
        MQTT.connectState = False
    
    def connect():
        while MQTT.connectState is not True:
            MQTT.connectState = True if MQTT.client.connect() == 0 else False
            time.sleep(1)
        try:
            MQTT.subTopic
            debug.print("resubscribe:",MQTT.subTopic)
            MQTT.sub(MQTT.subTopic,MQTT.callback)
        except:
            pass
        
    def pub(topic,msg):
        try:
            MQTT.client.publish(topic,msg)
        except OSError as e:
            print("reconnecting...")
            MQTT.client.connect(False)
            MQTT.sub(MQTT.subTopic,MQTT.callback)
            print("reconected.")

    def sub(topic,cb):
        MQTT.subTopic = topic
        MQTT.callback = cb
        MQTT.client.set_callback(cb)
        MQTT.client.subscribe(topic)

    def checkMsg():
        try:
            MQTT.client.check_msg()
        except OSError as e:
            print("reconnecting...")
            MQTT.client.connect(False)
            MQTT.sub(MQTT.subTopic,MQTT.callback)
            print("reconected.")

class WebEye():
    
    def init():
        WebEye.led = LED(4)
        WebEye.led.on(5)
        WebEye.led.blink(0.6)
        WebEye.cam = Camera
        WebEye.wifi = WiFi
        WebEye.mqtt = MQTT
        WebEye.wifi.setup('KingKit_2.4G','webduino')
        WebEye.mqtt.setup('mqtt1.webduino.io','webduino','webduino')
        
        
    def connect():
        WebEye.wifi.connect()
        WebEye.led.blink(0.25)
        WebEye.mqtt.connect()
        WebEye.led.blink(0)


class CamApp():
    def setUploadFolder(folderId,sendTime=2):
        GDriver.setFolderId(folderId)
        CamApp.sendTime = sendTime
    
    def getTime():
        _time = CamApp.rtc.datetime()
        MM =  _time[1]
        dd =  _time[2]
        hh =  _time[4]
        mm =  _time[5]
        ss =  _time[6]
        MM = "0"+str(MM) if MM < 10 else str(MM)
        dd = "0"+str(dd) if dd < 10 else str(dd)
        hh = "0"+str(hh) if hh < 10 else str(hh)
        mm = "0"+str(mm) if mm < 10 else str(mm)
        ss = "0"+str(ss) if ss < 10 else str(ss)
        return MM+"/"+dd+" "+hh+":"+mm+":"+ss
    
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
            if(msg==b'time'):
                CamApp.eye.mqtt.pub(CamApp.name+b'/state', CamApp.getTime())
        # 補光燈
        if(topic==(CamApp.name+b'/led')):
            try:
                CamApp.eye.led.on(int(msg))
            except:
                CamApp.eye.led.on(1000)
        # 拍照
        if(topic==(CamApp.name+b'/snapshot')):
            if(msg==b'now'):
                CamApp.snaping = True
                CamApp.eye.mqtt.pub((CamApp.name+b'/state'), b'waiting')
                image = CamApp.eye.cam.snapshot()
                CamApp.eye.mqtt.pub((CamApp.name+b'/state'), b'upload')
                filename = "snap-"+CamApp.getTime()
                print("time:",filename)
                GDriver.upload(CamApp.eye.cam.snapshot(),filename)
                CamApp.eye.mqtt.pub((CamApp.name+b'/state'), b'upload '+filename)
                CamApp.snaping = False

    def init(name,ssid,pwd):
        CamApp.name = str.encode(name)
        CamApp.wdt = WDT(timeout=3*60*1000)
        CamApp.snaping = False
        print("init CamApp...")
        CamApp.eye = WebEye
        CamApp.eye.init()
        print("cam init...")
        CamApp.eye.cam.init()
        if CamApp.eye.cam.initState == 1:
            print("connect...")
            # wifi & mqtt
            print("wifi & mqtt connect...")
            CamApp.eye.connect()
            CamApp.eye.mqtt.sub(CamApp.name+b'/#',CamApp.onMsg)
            CamApp.eye.mqtt.pub((CamApp.name+b'/state'), b'Ready')
            print("set ntptime & rtc")
            ntptime.NTP_DELTA = ntptime.NTP_DELTA - 8*60*60
            try:
                ntptime.settime()
            except:
                pass
            CamApp.rtc = machine.RTC()
            gc.collect()
            print("ready to go...")
            return True
        else:
            CamApp.eye.led.on(10)
            return False

    def run(enableDeepSleepMode=0):
        print("run...")
        now = 0
        min = CamApp.sendTime*60*10 # 5 min
        while True:
            CamApp.wdt.feed()
            if now % 100 == 0:
                CamApp.eye.mqtt.client.ping()
            if now == min or now == 0:
                print("Trigger....")
                now = 0
                try:
                    CamApp.eye.wifi.checkConnection()
                    CamApp.snaping = True
                    CamApp.eye.mqtt.pub((CamApp.name+b'/state'), b'waiting')
                    image = CamApp.eye.cam.snapshot()
                    CamApp.eye.mqtt.pub((CamApp.name+b'/state'), b'upload')
                    filename = CamApp.getTime()
                    GDriver.upload(CamApp.eye.cam.snapshot(),filename)
                    CamApp.eye.mqtt.pub((CamApp.name+b'/state'), b'upload '+filename)
                    CamApp.snaping = False
                    #直接重新開機
                    #machine.reset()
                except Exception as e:
                    CamApp.snaping = False
                    print("CamApp exception:",e)
            # enter deepsleep 5min
            if enableDeepSleepMode > 0:
                print("deep sleep:",enableDeepSleepMode,'mins')
                machine.deepsleep(enableDeepSleepMode*60*1000)
            if CamApp.snaping == False:
                CamApp.eye.mqtt.checkMsg()
            time.sleep(0.1)
            now = now + 1

try:

# wb129
    #    if CamApp.init('wb129','KingKit_2.4G','webduino'):
    #        CamApp.setUploadFolder('1f1wlSQG8qTbD79SXVsAmpvMtM_aP_GNk',sendTime=0)
    #        CamApp.run(enableDeepSleepMode = 9)

# battery
    #if CamApp.init('battery','KingKit_2.4G','webduino'):
    #    CamApp.setUploadFolder('1gwiQYeQ4N1r1WeHZRwtfhgNlHEDSBK8I',sendTime=0)
    #    CamApp.run(enableDeepSleepMode = 1)

#eye01
    #if CamApp.init('eye01','KingKit_2.4G','webduino'):
    #    CamApp.setUploadFolder('1DrhYTKccer3SSrxSzRxh2fQ-7CZBU01Z',sendTime=0)
    #    CamApp.run(enableDeepSleepMode = 1)

#eye02
    #if CamApp.init('eye02','KingKit_2.4G','webduino'):
    #    CamApp.setUploadFolder('1sRzVugTmOJEvJVXztWCVpNvk_Btn6aoq',sendTime=5)
    #    CamApp.run(enableDeepSleepMode = 0)


#wa001
    if CamApp.init('wa001','KingKit_2.4G','webduino'):
        CamApp.setUploadFolder('1oaJx5OUOK8FekcANGgr972thFjm-AFrv',sendTime=5)
        CamApp.run(enableDeepSleepMode = 5)


#home01 家裡中庭
#    if CamApp.init('home01','KingKit_2.4G','webduino'):
#        CamApp.setUploadFolder('14FQ5ICGN9i96EpGlbAABwiiRRKMe8ls3',sendTime=3)
#        CamApp.run(enableDeepSleepMode = 0)

#home02 
#    if CamApp.init('home02','KingKit_2.4G','webduino'):
#        CamApp.setUploadFolder('1HajUgrVmrG7Avo7mL2qFgmI_1HlLJeHc',sendTime=3)
#        CamApp.run(enableDeepSleepMode = 0)

#eye01 
#    if CamApp.init('eye01','KingKit_2.4G','webduino'):
#        CamApp.setUploadFolder('1MBPHqXUOY6wXYKu6q6x-GzdhL8msraNI',sendTime=10)
#        CamApp.run(enableDeepSleepMode = 0)

#bug01
#    if CamApp.init('bug01','KingKit_2.4G','webduino'):
#        CamApp.setUploadFolder('1X5fOnihYWiaSXPw8Cmeor55TSNV2nn0-',sendTime=5)
#        CamApp.run(enableDeepSleepMode = 0)

except Exception as e:
    print("init exception:",e)
    machine.reset()

