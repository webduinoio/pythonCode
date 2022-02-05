from webduino import Board
from uyeelight import Bulb
 
#####################
try:
    import cmd
    machine.reset()
except:
    pass
#####################

esp01 = Board("ws")
esp01.enableAP(ssid='smart')
esp01.connect()

bulb = Bulb("192.168.0.95")
bulb.set_rgb(255,2,2,duration=1)
bulb.turn_on()


