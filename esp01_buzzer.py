import os,machine,math,time
from machine import ADC, I2C, Pin

class Buzzer():
    # 262 294 330 349 392 440 494
    def __init__(self):
        self.queue = []
        self.isPause = False
        gnd = machine.Pin(1)
        gnd.off()

    def play(self,freq=300,delay=0.1):
        pin25 = machine.PWM(machine.Pin(3), duty=512)
        pin25.freq(freq)
        time.sleep(delay)
        machine.PWM(machine.Pin(3), duty=0)

    def playList(self,list):
        self.queue.extend(list)

    def pause(self,b):
        self.isPause = b

    def stop(self):
        self.queue = []

    def run(self):
        while True:
            if len(self.queue)>0 and not self.isPause:
                note = self.queue[0]
                del self.queue[0]
                self.play(note[0],note[1])

buzzer = Buzzer()              
buzzer.play(262,0.15)
buzzer.play(294,0.1)
buzzer.play(330,0.1)
buzzer.play(349,0.1)
buzzer.play(392,0.1)
buzzer.play(440,0.1)
buzzer.play(494,0.1)