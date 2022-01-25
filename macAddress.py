import network , ubinascii

mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode().replace(':','')
print(mac)