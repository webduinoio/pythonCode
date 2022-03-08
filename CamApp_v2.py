from webduino import Board
from machine import Pin, PWM, Timer, WDT
import usocket, ntptime, random, network, time, machine, camera, ubinascii, os

class GDriver:
    scriptId='AKfycbxhgMJ0MH74u2wJeevLmIJTC-cgBV3IuvtO_22mopfIdkjSfFXsbJE0DFDiuFKuyyiR'
    scriptCode = 'https://script.google.com/u/1/home/projects/1I29nq5NHfhvYjGlssJyFG1RfwbTrKdRr1VE_vX3kI5t76mmytqUHsiMd/edit'

    def setScriptId(scriptId):
        GDriver.scriptId = scriptId

    def setFolderId(folderId):
        GDriver.folderId = folderId
        
    def upload(image,filename):
        url = 'https://script.google.com/macros/s/'+GDriver.scriptId+'/exec'
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
        response = ""
        if len(l) > 2:
            reason = l[2].rstrip()
        while True:
            l = s.readline().decode("utf-8")
            if len(l)>9 and l[0:9]=='Location:': response = l[10:-2]
            if not l or l == "\r\n\r\n": break
        return response        


class LED:
    def __init__(self,pin,strong=100,pwm=True):
        self.pin = pin
        self.strong=strong
        self.state = False
        self.timer = None
        self.isBlink = False
        if pwm:
            self.pwm = PWM(Pin(pin))
            self.pwm.freq(1024)
            self.pwm.duty(0)
        self.off()
        
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


class CamApp():
    def setSendTime(sendTime=2):
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
        if(topic==(CamApp.name+b'/reset')):
            if(msg==b'reset'):
                machine.reset()
        # 狀態查詢
        if(topic==(CamApp.name+b'/state')):
            if(msg==b'ping'):
                CamApp.board.mqtt.pub(CamApp.name+b'/state', b'pong')
            if(msg==b'time'):
                CamApp.board.mqtt.pub(CamApp.name+b'/state', CamApp.getTime())
        # 補光燈
        if(topic==(CamApp.name+b'/led')):
            try:
                CamApp.led.on(int(msg))
            except:
                CamApp.led.on(1000)
        # 拍照
        if(topic==(CamApp.name+b'/snapshot')):
            if(msg==b'now'):
                CamApp.snapshot_upload('snap-')

    def init(board):
        CamApp.name = str.encode(board.devId)
        CamApp.wdt = WDT(timeout=3*60*1000)
        CamApp.snaping = False
        CamApp.led = LED(4)
        print("cam init...")
        CamApp.cam = Camera
        CamApp.cam.init()
        print("init CamApp...")
        CamApp.board = board
        CamApp.board.mqtt.sub(CamApp.name+b'/#',CamApp.onMsg)
        CamApp.board.mqtt.pub((CamApp.name+b'/state'), b'Ready')
        print("set ntptime & rtc")
        ntptime.NTP_DELTA = ntptime.NTP_DELTA - 8*60*60
        try:
            ntptime.settime()
        except:
            pass
        CamApp.rtc = machine.RTC()
        gc.collect()

    def snapshot_upload(pre):
        CamApp.snaping = True
        CamApp.board.mqtt.pub((CamApp.name+b'/state'), b'waiting')
        image = CamApp.cam.snapshot()
        CamApp.board.mqtt.pub((CamApp.name+b'/state'), b'upload')
        filename = pre+CamApp.getTime()
        data = GDriver.upload(CamApp.cam.snapshot(),filename)
        CamApp.board.mqtt.pub((CamApp.name+b'/state'), b'upload '+data)
        CamApp.snaping = False        

    def run(enableDeepSleepMode=0):
        print("run...")
        now = 0 #一開始先拍一張照片
        min = CamApp.sendTime * 60*10 #min
        while True:
            CamApp.wdt.feed()
            if now % 100 == 0:
                CamApp.board.mqtt.client.ping()
            if now == min or now == 0:
                print("Trigger....")
                now = 0
                try:
                    CamApp.board.wifi.checkConnection()
                    CamApp.snapshot_upload('')
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
                CamApp.board.mqtt.checkMsg()
            time.sleep(0.1)
            now = now + 1



#####################
try:
    import cmd
    machine.reset()
except:
    pass
#####################
try:
    flash = LED(4,strong=2)
    flash.off()
    led = LED(2)
    led.blink(0.5)
    time.sleep(2)
    board = Board(devId='nina')
    led.blink(0.25)
    GDriver.setScriptId('AKfycbxhgMJ0MH74u2wJeevLmIJTC-cgBV3IuvtO_22mopfIdkjSfFXsbJE0DFDiuFKuyyiR')
    GDriver.setFolderId('1L25XnMlt16zSA_6eUT0iYiO0LCWC3xzB')
    CamApp.init(board)
    led.blink(0)
    CamApp.setSendTime(sendTime=1)
    CamApp.run(enableDeepSleepMode = 0) # do not deepsleep
except Exception as e:
    print(e)
    print('')
    machine.reset()
