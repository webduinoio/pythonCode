import os

class Config:
    data = {}

    def show():
        print(Config.data)

    def put(key,val):
        Config.data[key] = val
        return Config

    def get(key):
        if key in Config.data:
            return Config.data[key]
        else:
            return None

    def remove(key):
        if key in Config.data:
            del Config.data[key]
            return True
        else:
            return False

    def updateFromString(data): 
        data = data.split('/')
        Config.data['ssid1'] = data[0]
        Config.data['passwd1'] = data[1]
        Config.data['ssid2'] = data[2]
        Config.data['passwd2'] = data[3]
        Config.data['ssid3'] = data[4]
        Config.data['passwd3'] = data[5]
        Config.data['devId'] = data[6]
        Config.data['devSSID'] = data[7]
        Config.data['devPasswd'] = data[8]
        Config.data['zone'] = data[9]
        Config.data['openAp'] = data[10]
        return Config.data

    def load(): 
        defaultData = "webduino.io/webduino/////unknown/webduino/12345678/global/No"
        data = None
        try:
            file = open('value.js','r')
            data = file.readline()
            Config.data = eval(data[9:])
            file.close()
        except:
            Config.updateFromString(defaultData)
            Config.save()
        return Config.data

    def save():
        file = open('value.js','w')
        data = "var data="+str(Config.data)
        file.write(data)
        file.close()
        return data


class JSONFile:
    
    def __init__(self,filename,default={}):
        self.filename = filename
        self.data = {}
        try:
            self.load()
        except:
            self.data = default
            self.save()

    def show(self):
        print(self.data)

    def put(self,key,val):
        self.data[key] = val
        return self

    def get(self,key):
        if key in self.data:
            return self.data[key]
        else:
            return None

    def remove(self,key):
        if key in self.data:
            del self.data[key]
            return True
        else:
            return False

    def load(self): 
        file = open(self.filename,'r')
        self.data = eval(file.readline())
        file.close()
        return self.data

    def save(self):
        file = open(self.filename,'w')
        file.write(str(self.data))
        file.close()
        return self.data
