from uyeelight import *

bulbs = Bulb.search(timeout=1)

if len(bulbs)==0:
    raise Exception("bulb not found.")

ip = list(bulbs.keys())[0]
bulb = Bulb(ip)
bulb.turn_on()
bulb.set_rgb(255,0,25, effect=EFFECT.SUDDEN, duration=0.1)
