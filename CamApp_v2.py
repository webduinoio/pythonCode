from webduino.board import Board
from webduino.config import JSONFile
from webduino.led import LED
from webduino.camera import Camera
from webduino.gdriver import GDriver

from machine import WDT
import ntptime,time, machine, urequests, gc, os

class CamApp():

    def getDefaultCfg():
        data = {}
        data['sendTime'] = 5
        data['enableCron'] = False
        data['folderId'] = '1c3fen96e5NFtzdRFMI1KnMc9XvqydjI9'
        data['scriptId'] = 'AKfycbxhgMJ0MH74u2wJeevLmIJTC-cgBV3IuvtO_22mopfIdkjSfFXsbJE0DFDiuFKuyyiR'
        return data
    
    def init(board):
        CamApp.name = board.devId
        CamApp.cfg = JSONFile('webeye.cfg',CamApp.getDefaultCfg())
        ##
        GDriver.scriptURL = CamApp.cfg.get('scriptId')
        GDriver.folderId = CamApp.cfg.get('folderId')
        CamApp.sendTime = CamApp.cfg.get('sendTime')
        CamApp.enableCron = CamApp.cfg.get('enableCron')
        ##
        CamApp.wdt = WDT(timeout=3*60*1000)
        CamApp.snaping = False
        CamApp.led = LED(4)
        print("cam init...")
        CamApp.cam = Camera
        CamApp.cam.init()
        print("init CamApp...")
        CamApp.board = board
        CamApp.board.mqtt.sub(CamApp.name+'/#',CamApp.onMsg)
        CamApp.board.publish(CamApp.name+'/state', 'ready '+str(CamApp.cfg.data))
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
                os.remove(CamApp.cfg.filename)
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
            CamApp.board.publish(CamApp.name+'/state', 'info '+str(CamApp.cfg.data))

        # 間隔時間 sendTime
        if(topic==(CamApp.name+'/sendTime')):
            CamApp.sendTime = int(msg)
            CamApp.cfg.put('sendTime',CamApp.sendTime)
            CamApp.cfg.save()
            CamApp.board.publish(CamApp.name+'/state', 'setOK sendTime')

        # 拍照 snapshot
        if(topic==(CamApp.name+'/snapshot')):
            CamApp.snapshot_upload('snap-')

        # 攝影開關 enableCron
        if(topic==(CamApp.name+'/enableCron')):
            CamApp.enableCron = bool(msg.replace('False',''))
            CamApp.cfg.put('enableCron',CamApp.enableCron)
            CamApp.cfg.save()
            CamApp.board.publish(CamApp.name+'/state', 'setOK enableCron')
            CamApp.now = 0

        # 雲端硬碟網址 folderId
        if(topic==(CamApp.name+'/folderId')):
            GDriver.folderId = msg
            CamApp.cfg.put('folderId',GDriver.folderId)
            CamApp.cfg.save()
            CamApp.board.publish(CamApp.name+'/state', 'setOK folderId')

        # 雲端硬碟腳本網址 scriptURL
        if(topic==(CamApp.name+'/scriptURL')):
            GDriver.scriptURL = msg
            CamApp.cfg.put('scriptURL',GDriver.scriptURL)
            CamApp.cfg.save()
            CamApp.board.publish(CamApp.name+'/state', 'setOK scriptURL')

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


#####################
try:
    import cmd
    machine.reset()
except:
    pass
#####################
try:
    time.sleep(2)
    CamApp.init(Board(devId='new'))
    CamApp.run(enableDeepSleepMode = 0) # 0 min: do not deepsleep
except Exception as e:
    print(e)
    print('')
    machine.reset()
