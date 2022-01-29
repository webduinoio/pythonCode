from machine import Pin
from utime import ticks_us, ticks_diff
from array import array
import time


def beep(t=1):
    beep = Pin(12,Pin.OUT)
    for i in range(t):
        beep.off()
        time.sleep(0.05)
        beep.on()
        time.sleep(0.05)



class RFBtn:
    
    def parseData(data):
        key = ''
        binKey = ''
        charKey = ''
        for i in data:
            if i > 800:
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
        nedges = 100
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
            #print("maxTime:",maxTime)
            if(maxTime >7000 and maxTime < 10000):
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

btn315_blue   = "659aaaaa5959"
btn315_red    = "6559a6996959"
btn315_yellow = "556a6555a959"
while True:
    data = RFBtn.listener(Pin(5,Pin.IN))
    print(data)
    if(len(data)==12):
        if(data==btn315_blue):
            beep(1)
            print("Btn Blue")
        if(data==btn315_yellow):
            beep(2)
            print("Btn Yellow")
        if(data==btn315_red):
            beep(3)
            print("Btn Red")
        
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
