from machine import Pin, I2C, SPI
import ssd1306, time, network
from sx127x import SX127x


OnboardLED = Pin(25, Pin.OUT)

time.sleep(1)
OnboardLED.value(not OnboardLED.value())
time.sleep(1)
OnboardLED.value(not OnboardLED.value())



class heltec:
    def init():
        ###
        heltec.device_config = {'miso':19,'mosi':27,'ss':18,'sck':5,'dio_0':35,'reset':14,'led':2}
        heltec.lora_parameters = {
            'frequency': 868E6, 'tx_power_level': 2, 
            'signal_bandwidth': 125E3,  'spreading_factor': 8, 
            'coding_rate': 5, 'preamble_length': 8,
            'implicit_header': False,'sync_word': 0x12, 
            'enable_CRC': False,'invert_IQ': False,
        }
        heltec.device_spi = SPI(baudrate=10000000,
                polarity=0, phase=0, bits=8, firstbit=SPI.MSB,
                sck = Pin(heltec.device_config['sck'], Pin.OUT, Pin.PULL_DOWN),
                mosi = Pin(heltec.device_config['mosi'], Pin.OUT, Pin.PULL_UP),
                miso = Pin(heltec.device_config['miso'], Pin.IN, Pin.PULL_UP))
        heltec.lora = SX127x(heltec.device_spi, pins=heltec.device_config, parameters=heltec.lora_parameters)        
        # Heltec LoRa 32 with OLED Display
        heltec.oled_width = 128
        heltec.oled_height = 64
        # OLED reset pin
        heltec.i2c_rst = Pin(16, Pin.OUT)
        # Initialize the OLED display
        heltec.i2c_rst.value(0)
        time.sleep_ms(5)
        heltec.i2c_rst.value(1) # must be held high after initialization
        # Setup the I2C lines
        heltec.i2c_scl = Pin(15, Pin.OUT, Pin.PULL_UP)
        heltec.i2c_sda = Pin(4, Pin.OUT, Pin.PULL_UP)
        # Create the bus object
        heltec.i2c = I2C(scl=heltec.i2c_scl, sda=heltec.i2c_sda)
        # Create the display object
        heltec.oled = ssd1306.SSD1306_I2C(heltec.oled_width, heltec.oled_height, heltec.i2c)        
        
    def fill(n):
        heltec.oled.fill(n)
        heltec.oled.show()
        
    def text(str,x,y):
        heltec.oled.text(str,x,y)
        heltec.oled.show()
        
    def line(x1,y1,x2,y2,bold):
        heltec.oled.line(x1,y1,x2,y2, bold)
        heltec.oled.show()


def receive(lora):
    print("LoRa Receiver")
    while True:
        if lora.received_packet():
            lora.blink_led()
            payload = lora.read_payload()
            heltec.fill(0)
            heltec.text('LoRa init...', 20, 5)
            heltec.text(payload, 20, 25)

heltec.init()
receive(heltec.lora)
heltec.text('LoRa init...', 20, 5)

