from webduino import Board

b = Board(devId='marty')
b.enableAP(ssid='wawo',pwd='12345678')
b.connect()