from webduino import Board
from machine import Pin, PWM
import time

#####################
try:
    import cmd
    machine.reset()
except:
    pass
#####################
time.sleep(2)

pwm = PWM(Pin(4))
pwm.freq(500) # def:500
pwm.duty(1)

board = Board(devId='home01')
print("start webcam...")
from esp32cam.webserver import webcam
server = webcam()
server.run()

pwm.duty(0)



