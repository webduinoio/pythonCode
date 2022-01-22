from hmc5883l import HMC5883L

sensor = HMC5883L(scl=0, sda=2)

for i in range(1000):
    x, y, z = sensor.read()
    print(sensor.format_result(x, y, z))