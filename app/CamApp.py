from webduino.board import Board
from webduino.config import JSONFile
from webduino.led import LED
from webduino.camera import Camera
from webduino.gdriver import GDriver

from machine import WDT
import ntptime,time, machine, urequests, gc, os, ubinascii, network

class CamApp():

    def getDefaultCfg():
        data = {}
        data['sendTime'] = 5
        data['enableCron'] = False
        data['folderId'] = '1c3fen96e5NFtzdRFMI1KnMc9XvqydjI9'
        data['scriptId'] = 'AKfycbxhgMJ0MH74u2wJeevLmIJTC-cgBV3IuvtO_22mopfIdkjSfFXsbJE0DFDiuFKuyyiR'
        return data
    
    def init(ledPin=4,deviceId=''):
        CamApp.cfg = JSONFile('webeye.cfg',CamApp.getDefaultCfg())
        ##
        GDriver.scriptURL = CamApp.cfg.get('scriptId')
        GDriver.folderId = CamApp.cfg.get('folderId')
        CamApp.sendTime = CamApp.cfg.get('sendTime')
        CamApp.enableCron = CamApp.cfg.get('enableCron')
        ##
        CamApp.wdt = WDT(timeout=3*60*1000)
        CamApp.snaping = False
        CamApp.led = LED(ledPin)
        CamApp.led.on()
        print("cam init...")
        CamApp.cam = Camera
        CamApp.cam.init()
        print("init board...")
        CamApp.led.blink(0.5)
        CamApp.board = Board(deviceId)
        CamApp.name = CamApp.board.devId
        CamApp.reg_cmd()
        #CamApp.board.setExtraCmdProcess(CamApp.camCmd)
        CamApp.board.publish(CamApp.name+'/state', 'ready '+str(CamApp.cfg.data))
        print("set RTC...")
        CamApp.setRTC()
        CamApp.led.blink(0)
        gc.collect()

    def reg_cmd():
        CamApp.board.onTopic("reboot",CamApp.cmd_reboot)
        CamApp.board.onTopic("clear",CamApp.cmd_clear)
        CamApp.board.onTopic("state",CamApp.cmd_state)
        CamApp.board.onTopic("led",CamApp.cmd_led)
        CamApp.board.onTopic("info",CamApp.cmd_info)
        CamApp.board.onTopic("sendTime",CamApp.cmd_sendTime)
        CamApp.board.onTopic("snapshot",CamApp.cmd_snapshot)
        CamApp.board.onTopic("enableCron",CamApp.cmd_enableCron)
        CamApp.board.onTopic("folderId",CamApp.cmd_folderId)
        CamApp.board.onTopic("scriptURL",CamApp.cmd_scriptURL)

    #重新開機
    def cmd_reboot(args):
        CamApp.board.publish(CamApp.name+'/state', 'reboot')
        time.sleep(1)
        machine.reset()        

    # 清除參數
    def cmd_clear(args):
        os.remove(CamApp.cfg.filename)
        CamApp.board.publish(CamApp.name+'/state', 'setOK clear')
    
    # 狀態查詢
    def cmd_state(args):
        if(args[0]=='ping'):
            CamApp.board.publish(CamApp.name+'/state', 'pong')
        if(args[0]=='time'):
            CamApp.board.publish(CamApp.name+'/state', CamApp.getTime())

    # 補光燈
    def cmd_led(args):
        try:
            CamApp.led.on(int(args[0]))
        except:
            CamApp.led.on(1000)

    # 取得資訊 info
    def cmd_info(args):
        CamApp.board.publish(CamApp.name+'/state', 'info '+str(CamApp.cfg.data))
    
    # 間隔時間 sendTime
    def cmd_sendTime(args):
        CamApp.sendTime = int(args[0])
        CamApp.cfg.put('sendTime',CamApp.sendTime)
        CamApp.cfg.save()
        CamApp.board.publish(CamApp.name+'/state', 'setOK sendTime')    

    # 拍照 snapshot
    def cmd_snapshot(args):
        CamApp.snapshot_upload('snap-')
        
    # 攝影開關 enableCron
    def cmd_enableCron(args):
        CamApp.enableCron = bool(args[0].replace('False',''))
        CamApp.cfg.put('enableCron',CamApp.enableCron)
        CamApp.cfg.save()
        CamApp.board.publish(CamApp.name+'/state', 'setOK enableCron')
        CamApp.now = 0
            
    # 雲端硬碟網址 folderId
    def cmd_folderId(args):
        GDriver.folderId = str(args).replace('?usp=sharing','')
        CamApp.cfg.put('folderId',GDriver.folderId)
        CamApp.cfg.save()
        CamApp.board.publish(CamApp.name+'/state', 'setOK folderId')

    # 雲端硬碟腳本網址 scriptURL
    def cmd_scriptURL(args):
        GDriver.scriptURL = args[0]
        CamApp.cfg.put('scriptURL',GDriver.scriptURL)
        CamApp.cfg.save()
        CamApp.board.publish(CamApp.name+'/state', 'setOK scriptURL')

    def setRTC():
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

    def snapshot_upload(pre):
        CamApp.snaping = True
        CamApp.board.publish((CamApp.name+'/state'), 'waiting')
        try:
            image = CamApp.cam.snapshot()
        except Exception as e:
            print(e)
            print('')
            CamApp.board.publish((CamApp.name+'/state'), 'except camera failure,reboot !')
            time.sleep(1)
            machine.reset()
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
            if CamApp.now % (5*60*10) == 0:
                CamApp.board.mqtt.client.ping()
            # debug
            if(CamApp.now%10==0):
                print(CamApp.name+': cronState:'+str(CamApp.enableCron)+' , '+str(int(CamApp.now/10))+'/'+str(int(min/10)))
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
                CamApp.board.check()
            time.sleep(0.1)
            CamApp.now = CamApp.now + 1 


#####################
try:
    import cmd
    machine.reset()
except:
    pass
#####################
try:
    CamApp.init(ledPin=2)
    CamApp.run(enableDeepSleepMode = 0) # 0 min: do not deepsleep
except Exception as e:
    print(e)
    print('')
    machine.reset()
