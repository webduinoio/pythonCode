from machine import Pin,I2C
import adxl345
import time

i2c = I2C(scl=Pin(4),sda=Pin(5), freq=10000)
adx = adxl345.ADXL345(i2c)
gnd = Pin(15,Pin.OUT)
gnd.off()

while True:
    x=adx.xValue
    y=adx.yValue
    z=adx.zValue
    #print('The acceleration info of x, y, z are:%d,%d,%d'%(x,y,z))
    roll,pitch = adx.RP_calculate(x,y,z)
    print('roll=',roll,'pitch=',pitch)
    if(abs(roll)<15 and abs(pitch)<15):
        print("1")
    elif(abs(roll)>165 and abs(pitch)<15):
        print("6")
    elif(pitch>-90 and pitch<-70):
        print("2")
    elif(roll<0 and abs(roll)>80 and abs(pitch)<10):
        print("3")
    elif(roll>70 and abs(pitch)<10):
        print("4")
    elif(pitch>70):
        print("5")
    time.sleep_ms(50)
