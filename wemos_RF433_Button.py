from machine import Pin
from utime import ticks_us, ticks_diff
from array import array
import time


def beep():
    beep = Pin(12,Pin.OUT)
    beep.off()
    time.sleep(0.1)
    beep.on()



class RFBtn:
    
    def parseData(data):
        key = ''
        binKey = ''
        charKey = ''
        for i in data:
            if i > 900:
                key = key + "1"
            else:
                key = key + "0"
            if(len(key)%8==0):
                c = chr(int(key, 2))
                charKey = charKey + c
                binKey = binKey + hex(int(key, 2))[2:]
                key = ''
        return binKey        

    def listener(p):
        nedges = 80
        state = 0
        while state < 2:
            x = 0
            state = 0
            diffs = []
            cycle = []
            times = array('I',  (0 for _ in range(nedges)))
            # 1.findout every change point
            while x < nedges:
                v = p()
                while v == p():
                    pass
                times[x] = ticks_us()
                x += 1
            # 2.calculate diffTime & boundle
            for x in range(nedges - 2):
                diffs.append(times[x + 1]- times[x])

            maxTime = max(diffs)*0.8
            if(maxTime >7000 and maxTime < 9000):
                #print("trigger:",maxTime)
                for i in diffs:
                    if(i > maxTime*0.8 and state == 0):
                        state = 1
                        #print("start:",i)
                    elif (i < maxTime and state == 1):
                        cycle.append(i)
                    elif (i > maxTime and state == 1):
                        state = 2
                        #print("end:",i)
                        break
                #print("state:",state)
                if(state==2):
                    return RFBtn.parseData(cycle)

print("start...")

btn1 = "5556565a5556"
btn2 = "5566959a5556"
btn3 = "5559565a5556"
btn4 = "555aa5aa5556"

while True:
    data = RFBtn.listener(Pin(5,Pin.IN))
    if(len(data)==12):
        beep()
        if(data==btn1):
            beep()
            print("Btn 1")
        if(data==btn2):
            beep()
            print("Btn 2")
        if(data==btn3):
            beep()
            print("Btn 3")
        if(data==btn4):
            beep()
            print("Btn 4")
