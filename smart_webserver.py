import socket
from webduino import *

def web_page(para):
  html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
  </head><body> <h1>ESP Web Server</h1> 
  <p>state: <strong>""" + para + """</strong></body></html>"""
  return html



esp01 = Board('webServer')
esp01.connect("KingKit_2.4G")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
  conn, addr = s.accept()
  print('Got a connection from %s' % str(addr))
  request = conn.makefile('r',512)

  print("proc...")
  request = str(request)
  #request = request[0:request.find('\\r\\n')]
  print('Content = %s' % request)
  # ?config=webduino.io/webduino/////wa5499/smart/12345678/global/No
  config = request.find('/?config=')
  response = web_page(str(config))
  conn.send('HTTP/1.1 200 OK\n')
  conn.send('Content-Type: text/html\n')
  conn.send('Connection: close\n\n')
  conn.sendall(response)
  conn.send('\n\n\n\n')
  conn.close()
  print("-=-=-=-=-= connection close ! =-=-=-=-=-=-")