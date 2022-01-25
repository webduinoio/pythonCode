from machine import I2C, Pin

#i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000) #wemos

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

print('Scan i2c bus...')
devices = i2c.scan()

if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:',len(devices))

  for device in devices:  
    print("Decimal address: ",device," | Hexa address: ",hex(device))