from machine import Pin, PWM, reset
pwm = PWM(Pin(2))
pwm.freq(1024)
pwm.duty(3)
import time, sys
print("wait interrupt")
time.sleep(0.5)
try:
    from webduino.board import Board
    print("init board...")
    Board(devId='')
except Exception as e:
    sys.print_exception(e)
    time.sleep(0.5)
    reset()