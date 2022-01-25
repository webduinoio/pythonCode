import d1motor, time
from machine import SoftI2C, Pin
i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=100000)
m0 = d1motor.Motor(0, i2c)
m1 = d1motor.Motor(1, i2c)
m0.speed(50)
#m1.speed(500)
time.sleep(2)
m0.brake()
#m0.brake()
