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
            config = self.board.config.toJSON(config)
            self.board.config.saveJSON(config)
            self.board.config.update(self.board)
            cs.send("Save OK") 
        cs.close() 

    def processGet(self,cs,req):
        cs.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        try:
            filename = req['url'][1][1:]
            if(filename=='favicon.ico'):
                raise Exception("no process",filename)
            if filename == '':
                filename = 'index.html'
            file = open(filename, "r")
            while True:
                line = file.readline()
                time.sleep(0.02)
                if(line==""):
                    break
                cs.send(line)
            file.close()         
        except Exception as e:
            print("Error:",e)
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
        while True:
            line = cl_file.readline()
            #print("line:",line)
            if not line or line == b'\r\n':
                break
            if len(line)>18 and str(line).find('Content-Length:')>=0:
                req['Content-Length'] = int(str(line)[18:-5])
            if len(line)>4 and (line[0:5]==b'GET /' or line[0:6]==b'POST /'):
                req['url'] = str(line).split(' ')
        print("request:",req['url'])
        if(req['url'][1] is '/save'):
            self.processPost(cs,req)
        else:
            self.processGet(cs,req)        

    def listener(self):
        self.ss.setsockopt(socket.SOL_SOCKET, 20, self.acceptSocket)

