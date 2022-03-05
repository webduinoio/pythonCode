import socket, time

class WebServer:  
    
    def __init__(self,board,port=80):
        self.addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
        self.ss = socket.socket()
        self.ss.bind(self.addr)
        self.ss.listen(1)
        self.board = board

    def unquote(self,string):
        _hextobyte_cache = None
        if not string:
            return b''
        if isinstance(string, str):
            string = string.encode('utf-8')
        bits = string.split(b'%')
        if len(bits) == 1:
            return string
        res = [bits[0]]
        append = res.append
        if _hextobyte_cache is None:
            _hextobyte_cache = {}
        for item in bits[1:]:
            try:
                code = item[:2]
                char = _hextobyte_cache.get(code)
                if char is None:
                    char = _hextobyte_cache[code] = bytes([int(code, 16)])
                append(char)
                append(item[2:])
            except KeyError:
                append(b'%')
                append(item)
        return b''.join(res)
 
    def processPost(self,cs,req):
        cs.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl_file = req['stream']
        contentLen = req['Content-Length']
        urlPage = req['url'][1]
        formData = cl_file.read(contentLen)
        if(urlPage == '/save'):
            config = self.unquote(formData).decode("utf-8")[7:]
            self.board.config.updateFromString(config)
            self.board.config.save()
            cs.send("Save OK") 
        cs.close() 

    def processGet(self,cs,req):
        #print("processGet...")
        cs.sendall('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')        
        try:
            print("process:"+str(req['url']))
            filename = req['url'][1][1:]
            if(filename=='favicon.ico'):
                print("> no process:"+filename)
                #raise Exception("no process",filename)
            if filename == '':
                filename = 'index.html'
            if filename == 'value.js':
                config = self.board.config.data
                config['AP'] = self.board.ap()
                config['IP'] = self.board.ip()
                config['MAC'] = self.board.mac()
                config['Ver'] = self.board.Ver
                #print("resp:",str(config))
                cs.send("var data="+str(config))
            else:
                #print("open file:"+filename)
                file = open(filename, "r")
                while True:
                    line = file.readline()
                    cs.sendall(line)
                    if(line==""):
                        break
                file.close()         
        except Exception as e:
            print("Error: "+filename)
            pass
        cs.close()

    def acceptSocket(self,sc):
        #print("obj1:",sc)
        cs, addr = self.ss.accept()
        req = {}
        contentLen = None
        #print('client connected from', addr)
        cl_file = cs.makefile('rwb', 0)
        req['stream'] = cl_file
        test = ''
        while True: 
            line = cl_file.readline().decode("utf-8")
            #print("line:",line)
            if not line or line == '\r\n':
                break 
            if len(line)>18 and str(line).find('Content-Length:')>=0:
                #print("contentLen:",line)
                req['Content-Length'] = int(line[16:])
            if len(line)>4 and (line[0:5]=='GET /' or line[0:6]=='POST /'):
                req['url'] = line.split(' ')

        #print("request:",req)

        if(req['url'][0] == "POST"):
            self.processPost(cs,req)
            
        elif(req['url'][0] == "GET"):
            self.processGet(cs,req)        

    def listener(self):
        self.ss.setsockopt(socket.SOL_SOCKET, 20, self.acceptSocket)
