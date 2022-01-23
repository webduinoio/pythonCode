import time
import mlx90614
from machine import I2C, Pin
from uyeelight import *

bulbs = Bulb.search(timeout=1)

if len(bulbs)==0:
    raise Exception("bulb not found.")

ip = list(bulbs.keys())[0]
bulb = Bulb(ip)
bulb.turn_on()
bulb.set_rgb(255,255,255, effect=EFFECT.SUDDEN, duration=0.1)
time.sleep(1)
bulb.set_rgb(255,100,0, effect=EFFECT.SUDDEN, duration=0.1)


i2c = I2C(scl=Pin(2), sda=Pin(0))
sensor = mlx90614.MLX90614(i2c)

while True:
    ambient = sensor.read_ambient_temp()
    objTemp = sensor.read_object_temp()
    print(objTemp*10)
    bulb.set_rgb(255,0,objTemp*10, effect=EFFECT.SUDDEN, duration=0.1)
    time.sleep_ms(100)