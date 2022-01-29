from machine import TouchPad, Pin
import time

#ten capacitive touch-enabled pins: 0, 2, 4, 12, 13 14, 15, 27, 32, 33
"""
| MicroSD            |   ESP32 |
|:------------------ | -------:|
| DATA2              | GPIO 12 |
| DATA3              | GPIO 13 |
| CMD                | GPIO 15 |
| CLK                | GPIO 14 |
| DATA0              | GPIO  2 |
| DATA1 / flashlight | GPIO  4 |
"""
#esp32cam (x): t2,t13,t15 , (o): t12,t14

t12 = TouchPad(Pin(12))
t13 = TouchPad(Pin(13))
t15 = TouchPad(Pin(15))
t14 = TouchPad(Pin(14))
for i in range(100):
    print(t12.read(),t14.read())
    time.sleep(0.2)