from webduino import Board,Config
from machine import Pin, PWM, Timer, WDT
import usocket, ntptime, random, network, time, machine, camera, ubinascii, os
import urequests

class GDriver:
    scriptId='AKfycbxhgMJ0MH74u2wJeevLmIJTC-cgBV3IuvtO_22mopfIdkjSfFXsbJE0DFDiuFKuyyiR'
    scriptCode = 'https://script.google.com/u/1/home/projects/1I29nq5NHfhvYjGlssJyFG1RfwbTrKdRr1VE_vX3kI5t76mmytqUHsiMd/edit'

    def setScriptURL(scriptURL):
        GDriver.scriptURL = scriptURL

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
        msg = msg.decode("utf-8")
        topic = topic.decode("utf-8")
        print("onMsg:",topic+" , "+msg)

        # 重開機
        if(topic==(CamApp.name+'/reboot')):
            if(msg=='reset'):
                CamApp.board.publish(CamApp.name+'/state', 'reboot')
                time.sleep(1)
                machine.reset()

        # 清除參數
        if(topic==(CamApp.name+'/clear')):
            if(msg=='clear'):
                Config.remove('webeye')
                Config.save()
                CamApp.board.publish(CamApp.name+'/state', 'setOK clear')

        # 狀態查詢
        if(topic==(CamApp.name+'/state')):
            if(msg=='ping'):
                CamApp.board.publish(CamApp.name+'/state', 'pong')
            if(msg=='time'):
                CamApp.board.publish(CamApp.name+'/state', CamApp.getTime())

        # 補光燈
        if(topic==(CamApp.name+'/led')):
            try:
                CamApp.led.on(int(msg))
            except:
                CamApp.led.on(1000)

        # 取得資訊 info
        if(topic==(CamApp.name+'/info')):
            CamApp.board.publish(CamApp.name+'/state', 'info '+str(webeye))

        # 間隔時間 sendTime
        if(topic==(CamApp.name+'/sendTime')):
            webeye['sendTime'] = CamApp.sendTime = int(msg)
            Config.put('webeye',webeye)
            Config.save()
            CamApp.board.publish(CamApp.name+'/state', 'setOK sendTime')

        # 拍照 snapshot
        if(topic==(CamApp.name+'/snapshot')):
            CamApp.snapshot_upload('snap-')

        # 攝影開關 enableCron
        if(topic==(CamApp.name+'/enableCron')):
            webeye['enableCron'] = CamApp.enableCron = bool(msg.replace('False',''))
            Config.put('webeye',webeye)
            Config.save()
            CamApp.board.publish(CamApp.name+'/state', 'setOK enableCron')
            CamApp.now = 0

        # 雲端硬碟網址 folderId
        if(topic==(CamApp.name+'/folderId')):
            webeye['folderId'] = GDriver.folderId = msg
            Config.put('webeye',webeye)
            Config.save()
            CamApp.board.publish(CamApp.name+'/state', 'setOK folderId')

        # 雲端硬碟腳本網址 scriptURL
        if(topic==(CamApp.name+'/scriptURL')):
            webeye['scriptURL'] = GDriver.scriptURL = msg
            Config.put('webeye',webeye)
            Config.save()
            CamApp.board.publish(CamApp.name+'/state', 'setOK scriptURL')

    def init(board):
        CamApp.name = board.devId
        CamApp.wdt = WDT(timeout=3*60*1000)
        CamApp.snaping = False
        CamApp.led = LED(4)
        print("cam init...")
        CamApp.cam = Camera
        CamApp.cam.init()
        print("init CamApp...")
        CamApp.board = board
        CamApp.board.mqtt.sub(CamApp.name+'/#',CamApp.onMsg)
        CamApp.board.publish(CamApp.name+'/state', 'ready '+str(webeye))
        print("set ntptime & rtc")
        ntptime.NTP_DELTA = ntptime.NTP_DELTA - 8*60*60
        setNTPTime = False
        while(not setNTPTime):
            try:
                ntptime.settime()
                setNTPTime = True
            except Exception as e:
                print("ntptime error !")
                print(e)
        CamApp.rtc = machine.RTC()
        gc.collect()

    def snapshot_upload(pre):
        CamApp.snaping = True
        CamApp.board.publish((CamApp.name+'/state'), 'waiting')
        image = CamApp.cam.snapshot()
        CamApp.board.publish((CamApp.name+'/state'), 'uploading')
        filename = pre+CamApp.getTime()
        redirectURL = GDriver.upload(CamApp.cam.snapshot(),filename)
        fileInfo=urequests.get(redirectURL)
        CamApp.board.publish((CamApp.name+'/state'), 'upload '+str(fileInfo.json()))
        CamApp.snaping = False        

    def run(enableCron=True,enableDeepSleepMode=0):
        print("run...")
        CamApp.now = 0 #一開始先拍一張照片
        while True:
            CamApp.wdt.feed()
            min = CamApp.sendTime * 60*10 #min
            if CamApp.now % 100 == 0:
                CamApp.board.mqtt.client.ping()
            # debug
            if(CamApp.now%10==0):
                print('cronState:'+str(CamApp.enableCron)+' , '+str(int(CamApp.now/10))+'/'+str(int(min/10)))
            # check upload
            if CamApp.enableCron and (CamApp.now == min or CamApp.now == 0):
                print("Trigger....")
                CamApp.now = 0
                try:
                    CamApp.board.wifi.checkConnection('')
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
            # checkMsg if without snapping
            if CamApp.snaping == False:
                CamApp.board.mqtt.checkMsg()
            time.sleep(0.1)
            CamApp.now = CamApp.now + 1


webeye = {}

#####################
try:
    import cmd
    machine.reset()
except:
    pass
#####################
try:
    flash = LED(4,strong=5)
    flash.blink(0.25)
    led = LED(2)
    led.blink(0.5)
    time.sleep(2)
    board = Board(devId='webeye01')
    led.blink(0.25)
    ##
    if Config.get('webeye') == None:
        webeye['enableCron'] = False
        webeye['sendTime'] = 5
        webeye['folderId'] = '1L25XnMlt16zSA_6eUT0iYiO0LCWC3xzB'
        webeye['scriptId'] = 'AKfycbxhgMJ0MH74u2wJeevLmIJTC-cgBV3IuvtO_22mopfIdkjSfFXsbJE0DFDiuFKuyyiR'
        Config.put('webeye',webeye)
        Config.save()
    else:
        webeye = Config.get('webeye')
    ##
    GDriver.scriptURL = webeye['scriptId']
    GDriver.folderId = webeye['folderId']
    ##
    CamApp.init(board)
    led.blink(0)
    flash.blink(0)
    CamApp.folderId = webeye['folderId']
    CamApp.sendTime = webeye['sendTime']
    CamApp.enableCron = webeye['enableCron']
    CamApp.run(enableDeepSleepMode = 0) # do not deepsleep

except Exception as e:
    print(e)
    print('')
    machine.reset()
