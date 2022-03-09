from webduino import Board
from machine import Pin, PWM, Timer, WDT
import usocket, ntptime, random, network, time, machine, camera, ubinascii, os

board = Board(devId='test')
