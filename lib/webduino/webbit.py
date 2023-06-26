import machine,neopixel,time
from machine import Pin
import os,machine,math
from machine import ADC, I2C, Pin
from neopixel import NeoPixel
from webduino.board import Board
from webduino.debug import debug
from webduino.image import get_array

class Temp():
    def __init__(self):
        self.voltagePower = 3.3
        self.Rs = 10000   # 更改 Rs 的值，根據您的熱敏電阻的規格表
        self.B = 3950
        self.T0 = 273.15
        self.R1 = 2500   # 更改 R1 的值，根據傳感器上的參考電阻的規格表
        self.__temp__ = ADC(Pin(14)) # 溫度傳感器
        self.__temp__.atten(ADC.ATTN_11DB)
        self.lastTemp = 0

    def read(self):
        self.voltageValue = (self.__temp__.read() / 4095) * self.voltagePower
        self.Rt = ((self.voltagePower - self.voltageValue) * self.Rs) / self.voltageValue
        try:
            T = 1 / ((1 / self.T0) + (1 / self.B) * math.log(self.Rt*2 / self.R1))
            self.lastTemp = T - self.T0
        except:
            pass
        return self.lastTemp
    
class Btn():
    def __init__(self,pinNum):
        # A:35 , B:27
        self.btn = Pin(pinNum, Pin.IN)
        self.down = False
        self.up = False

    def isDown(self):
        down = self.btn.value() == 0
        if down:
            if self.down:
                return False
            self.down = True
            self.up = True
            return self.down
        else:
            if self.down:
                self.down = False
            return False

    def isUp(self):
        if self.btn.value() == 1 and self.up:
            self.up = False
            return True
        return False


class Buzzer:
    # 262 294 330 349 392 440 494
    def __init__(self):
        self.queue = []

    def playOne(self, freq=300, duration=0.1):
        if freq == 0: freq = 1
        pin17 = machine.PWM(machine.Pin(17), freq=freq, duty=512)
        if(duration==-1):
            return
        if(duration>=10):
            duration = duration/1000.0
        time.sleep(duration)
        machine.PWM(machine.Pin(17), duty=0)

    def playList(self, lst):
        self.queue.extend(lst)

    def stop(self):
        self.queue = []
        self.playOne(1,10)

    def run(self):
        while len(self.queue) > 0:
            note = self.queue[0]
            del self.queue[0]
            if isinstance(note, int):
                duration = self.queue[0]
                del self.queue[0]
                self.playOne(note,duration)
            else:
                self.playOne(note[0], note[1])

    def play(self, *args):
        if len(args) == 1 and isinstance(args[0], list):
            # Input: [ [freq1, delay1], [freq2, delay2], ... ]
            #print('1')
            for i in args:
                self.queue.extend(args[0])
            print(self.queue)
        elif len(args) == 1 and isinstance(args[0], int):
            self.playOne(args[0],-1)
        elif len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], (int, float)):
            # Input: freq, delay
            #print('2')
            self.queue.append([args[0], args[1]])
        self.run()


class RGB:
    def __init__(self,wbit,num):
        self.num = num
        self.wbit = wbit
    def color(self,r,g,b):
        self.wbit.show(self.num,r,g,b)
    def off(self):
        self.wbit.show(self.num,0,0,0)
        
class WebBit:

    def close(self):
        pass
    
    def disconnect(self):
        pass
    
    def createRGB(self):
        self.rgb = []
        for i in range(25):
            self.rgb.append(RGB(self,i))
    
    def __init__(self):
        self.np = neopixel.NeoPixel(machine.Pin(18), 25)
        self.buzzer = Buzzer()
        self.a = Btn(38)
        self.b = Btn(33)
        self.lL = ADC(Pin(12))
        self.rL = ADC(Pin(13))
        self.lL.atten(ADC.ATTN_6DB)
        self.rL.atten(ADC.ATTN_6DB)
        self._temp = Temp()
        self.showAll(0,0,0)
        self.beep()
        self.debug = debug
        self.wled = {0:20,1:15,2:10,3:5,4:0,5:21,6:16,7:11,8:6,9:1,10:22,11:17,12:12,13:7,14:2,15:23,16:18,17:13,18:8,19:3,20:24,21:19,22:14,23:9,24:4}
        self.online = False
        self.createRGB()

    def sub(self,topic,cb):
        self.connect()
        self.board.onTopic(topic,cb)

    def pub(self,topic,msg):
        self.connect()
        self.board.pub(topic,str(msg))
        
    def connect(self):
        if self.online == True: return
        self.showAll(20,0,0)
        try:
            self.board = Board(devId='bitv2')
        except:
            machine.reset()
        self.showAll(0,0,0)
        self.online = True

    def checkMsg(self):
        self.connect()
        self.board.mqtt.checkMsg()

    def readTemp(self):
        return self._temp.read()

    def temp(self):
        return self._temp.read()

    def leftLight(self):
        return self.lL.read()

    def rightLight(self):
        return self.rL.read()

    def readLeftLight(self):
        return self.lL.read()

    def readRightLight(self):
        return self.rL.read()

    def btnA(self):
        return self.a.btn.value() == 0

    def btnB(self):
        return self.b.btn.value() == 0

    def play(self, *args):
        self.buzzer.play(*args)
        
    def buzz(self, *args):
        self.buzzer.play(*args)
        
    def tone(self, *args):
        self.buzzer.play(*args)
        
    def beep(self, *args):
        if(len(args)==0):
            self.buzzer.play(500,100)
        else:
            self.buzzer.play(*args)

    def clear(self):
        self.showAll(0,0,0)

    def showAll(self,r,g,b):
        r = int(r / 10)
        g = int(g / 10)
        b = int(b / 10)
        for led in range(25):
            self.np[led] = (r,g,b)
        self.np.write()

    def show(*args):
        num_args = len(args)
        self = args[0]
        num = args[1]
        r = args[2]
        g = args[3]
        b = args[4]
        brightness = 1
        if(num_args==6):
            brightness = args[5]/100.0
        r = int(r / 10 * brightness)
        g = int(g / 10 * brightness)
        b = int(b / 10 * brightness)
        self.np[num] = (r,g,b)
        self.np.write()
    
    def matrix(self,r,g,b,data):
        matrix = [[int(data[i*5 + j]) for j in range(5)] for i in range(5)]
        reversed_matrix = [list(reversed(row)) for row in matrix]
        transposed_matrix = [[reversed_matrix[j][i] for j in range(5)] for i in range(5)]
        data = "".join(str(transposed_matrix[i][j]) for i in range(5) for j in range(5))
        for i in range(len(data)):
            if data[i] == '0':
                self.show(i, 0, 0, 0)
            elif data[i] == '1':
                self.show(i, r, g, b)

    def draw(self,data):
        self.showAll(0,0,0)
        for i in range(0, len(data), 8):
            num = int(data[i:i+2],16) # 燈號
            num = self.wled[num]
            hex_color = data[i+2:i+8] # 顏色
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            self.show(num, r, g, b)

    def sleep(self,i):
        time.sleep(i)

    def scroll(self, r, g, b, scroll_data, delay=0.2):
        # 跑馬燈 5x5 陣列
        scroll_string = ["", "", "", "", ""]
        # 要顯示的資料串再一起
        for i in range(0, 5):
            scroll_string[i] = (
                "".join(get_array(char)[i] for char in scroll_data)
                if type(scroll_data) == str
                else "".join(get_array(image)[i] for image in scroll_data)
            )
        # 至少要刷新 6 次把最後一次螢幕沒刷新的資料清掉
        for _ in range(0, len(scroll_data) * 5 + 1):
            # 資料處理
            data = (
                scroll_string[0][0:5]
                + scroll_string[1][0:5]
                + scroll_string[2][0:5]
                + scroll_string[3][0:5]
                + scroll_string[4][0:5]
            )
            matrix = [[int(data[i * 5 + j]) for j in range(5)]
                      for i in range(5)]
            reversed_matrix = [list(reversed(row)) for row in matrix]
            transposed_matrix = [
                [reversed_matrix[j][i] for j in range(5)] for i in range(5)
            ]
            data = "".join(
                str(transposed_matrix[i][j]) for i in range(5) for j in range(5)
            )
            for i in range(len(data)):
                if data[i] == "0":
                    self.np[i] = (0, 0, 0)
                elif data[i] == "1":
                    self.np[i] = (r, g, b)
            self.np.write()
            # 整個 5x5 陣列往左 shift 1 bit，最後面補 0
            for array_index in range(0, 5):
                scroll_string[array_index] = scroll_string[array_index][1:] + "0"
            self.sleep(delay)
        self.clear()
