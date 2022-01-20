import network,time

def do_connect():
    global connected
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    print('connecting to network...')
    sta_if.connect('webduino', 'webduino')
    cnt = 0
    while not sta_if.isconnected():
        cnt = cnt + 1
        time.sleep(0.5)
        if cnt == 20:
            break
    connected = sta_if.isconnected()
    print('network config:', sta_if.ifconfig())

print("connect...")
do_connect()
######
import upip
upip.install("umqtt.simple", "lib")
upip.install("micropython-uasyncio", "lib")
upip.install("micropython-urequests", "lib")
print("installed !")