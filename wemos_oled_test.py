from machine import Pin,I2C
import time, ssd1306


while True:
    try:
        i2c = I2C(scl=Pin(2), sda=Pin(0), freq=100000)
        lcd = ssd1306.SSD1306_I2C(128,64,i2c)
        lcd.text("abcdefghijklmno",0,3)
        lcd.text("012345678901234",0,13)
        lcd.text("012345678901234",0,23)
        lcd.text("012345678901234",0,33)
        lcd.text("012345678901234",0,43)
        lcd.text("012345678901234",0,53)
        lcd.show()
        time.sleep(1)
    except:
        pass


