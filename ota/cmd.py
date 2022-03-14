import os,machine
from utils import *
from webduino.board import Board

try:
    os.remove('cmd.py')
except:
    pass

Board(devId="ota")
url = 'https://marty5499.github.io/pythonCode/'
Utils.save(url+'lib/urequests.py','lib/urequests.py')
Utils.save(url+'lib/umqtt/simple.py','lib/umqtt/simple.py')
Utils.save(url+'lib/webduino/led.py','lib/webduino/led.py')
Utils.save(url+'lib/webduino/config.py','lib/webduino/config.py')
Utils.save(url+'lib/webduino/gdriver.py','lib/webduino/gdriver.py')
Utils.save(url+'lib/webduino/camera.py','lib/webduino/camera.py')
Utils.save(url+'lib/webduino/board.py','lib/webduino/board.py')
Utils.save(url+'lib/webduino/mqtt.py','lib/webduino/mqtt.py')
Utils.save(url+'lib/webduino/wifi.py','lib/webduino/wifi.py')
Utils.save(url+'lib/webduino/webserver.py','lib/webduino/webserver.py')
Utils.save(url+'lib/webduino/debug.py','lib/webduino/debug.py')
Utils.save(url+'lib/utils.py','lib/utils.py')
Utils.save(url,'index.html')
