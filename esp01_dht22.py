import dht, machine

d = dht.DHT22(machine.Pin(2))

print('d.measure():',d.measure())
print('d.temperature():',d.temperature())
print('d.humidity():',d.humidity())


