import network , time
from machine import Timer
from webduino.debug import debug


class WiFi:
    onlineCallback = None
    ssid="webduino.io"
    pwd="webduino"
    ip="unknown"
    
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
        if not WiFi.sta.isconnected():
            WiFi.connect(WiFi.ssid,WiFi.pwd)
            debug.print("!!!! online callback... !!!!")
        return WiFi.sta.isconnected()

    def enableAP(ssid="myboard",pwd="12345678"):
        WiFi.ap = network.WLAN(network.AP_IF)
        WiFi.ap.active(True)
        WiFi.ap.config(essid=ssid,password=pwd,authmode=3)

    def connect(ssid="webduino.io",pwd="webduino"):
        WiFi.ssid = ssid
        WiFi.pwd = pwd
        WiFi.sta = sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        sta_if.disconnect()
        debug.print('connecting to network...',WiFi.ssid)
        if(not sta_if.isconnected()):
            sta_if.connect(ssid,pwd)
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
