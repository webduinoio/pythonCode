import os

file = open("index.html", "r")
while True:
    line = file.readline()
    if(line==""):
        break
    print(">>>",line)
file.close() 