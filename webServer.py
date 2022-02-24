from webduino import Board
from uyeelight import Bulb
 
#####################
try:
    import cmd
    machine.reset()
except:
    pass
#####################

waboard = Board(devId="waboard")
waboard.enableAP()
waboard.connect()
print(waboard.ip())

"""
bulb = Bulb("192.168.0.95")
bulb.set_rgb(255,2,2,duration=1)
bulb.turn_on()
"""
