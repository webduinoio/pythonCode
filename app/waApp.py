from webduino.board import Board
from webduino.led import LED
import ntptime,time, machine, urequests, gc, os

#####################
try:
    import cmd
    machine.reset()
except:
    pass
#####################
try:
    print("==")
    print("-=-=-=-= base =-=-=-=-")
    print("==")
    board = Board(devId='0314')
    board.loop()
except Exception as e:
    print(e)
    print('')
    machine.reset()