import ssd1306
from machine import Pin, I2C
import time
import network
OnboardLED = Pin(25, Pin.OUT)

time.sleep(1)
OnboardLED.value(not OnboardLED.value())
time.sleep(1)
OnboardLED.value(not OnboardLED.value())

wlan = network.WLAN(network.STA_IF) # create station interface
wlan.active(True)       # activate the interface
wlan.isconnected()      # check if the station is connected to an AP
time.sleep_ms(500)
if not wlan.isconnected():
  print('connecting to network...')
  wlan.connect('webduino.io', 'webduino') # connect to an AP
  time.sleep_ms(500)
  while not wlan.isconnected():
    pass
print('network config:', wlan.ifconfig())

# Heltec LoRa 32 with OLED Display
oled_width = 128
oled_height = 64
# OLED reset pin
i2c_rst = Pin(16, Pin.OUT)
# Initialize the OLED display
i2c_rst.value(0)
time.sleep_ms(5)
i2c_rst.value(1) # must be held high after initialization
# Setup the I2C lines
i2c_scl = Pin(15, Pin.OUT, Pin.PULL_UP)
i2c_sda = Pin(4, Pin.OUT, Pin.PULL_UP)
# Create the bus object
i2c = I2C(scl=i2c_scl, sda=i2c_sda)
# Create the display object
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
oled.fill(0)
oled.text(wlan.ifconfig()[0], 0, 0)
oled.text('HELLO WiFi ESP32', 0, 25)
oled.text('escapequotes.net', 0, 55)
  
#oled.line(0, 0, 50, 25, 1)
oled.show()