import os
import usocket
import network,time
import network , ubinascii

def do_connect():
    global connected
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    print('connecting to network...')
    sta_if.connect('webduino.io', 'webduino')
    cnt = 0
    while not sta_if.isconnected():
        cnt = cnt + 1
        time.sleep(0.5)
        if cnt == 60:
            break
    connected = sta_if.isconnected()
    print('network config:', sta_if.ifconfig())

class Response:

    def __init__(self, f):
        self.raw = f
        self.encoding = "utf-8"
        self._cached = None

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.raw.read()
            finally:
                self.raw.close()
                self.raw = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        import ujson
        return ujson.loads(self.content)


def request(method, url, data=None, json=None, headers={}, stream=None):
    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""
    if proto == "http:":
        port = 80
    elif proto == "https:":
        import ussl
        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)
    #print("host:",host,",port:",port)
    ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
    ai = ai[0]

    s = usocket.socket(ai[0], ai[1], ai[2])
    try:
        s.connect(ai[-1])
        if proto == "https:":
            s = ussl.wrap_socket(s, server_hostname=host)
        s.write(b"%s /%s HTTP/1.0\r\n" % (method, path))
        if not "Host" in headers:
            s.write(b"Host: %s\r\n" % host)
        # Iterate over keys to avoid tuple alloc
        for k in headers:
            s.write(k)
            s.write(b": ")
            s.write(headers[k])
            s.write(b"\r\n")
        if json is not None:
            assert data is None
            import ujson
            data = ujson.dumps(json)
            s.write(b"Content-Type: application/json\r\n")
        if data:
            s.write(b"Content-Length: %d\r\n" % len(data))
        s.write(b"\r\n")
        if data:
            s.write(data)

        l = s.readline()
        #print(l)
        l = l.split(None, 2)
        status = int(l[1])
        reason = ""
        if len(l) > 2:
            reason = l[2].rstrip()
        while True:
            l = s.readline()
            if not l or l == b"\r\n":
                break
            #print(l)
            if l.startswith(b"Transfer-Encoding:"):
                if b"chunked" in l:
                    raise ValueError("Unsupported " + l)
            elif l.startswith(b"Location:") and not 200 <= status <= 299:
                raise NotImplementedError("Redirects not yet supported")
    except OSError:
        s.close()
        raise

    resp = Response(s)
    resp.status_code = status
    resp.reason = reason
    return resp


def head(url, **kw):
    return request("HEAD", url, **kw)

def get(url, **kw):
    print(">>>get>>>>",url)
    return request("GET", url, **kw)

def post(url, **kw):
    return request("POST", url, **kw)

def put(url, **kw):
    return request("PUT", url, **kw)

def patch(url, **kw):
    return request("PATCH", url, **kw)

def delete(url, **kw):
    return request("DELETE", url, **kw)


class Res:

    def save(url,file):
        try:
            response = get(url)
            print(">>",len(response.text) )
            print("get file:",file,'size:',len(response.text),',save to:',file)
            f = open(file, 'w')
            f.write(response.text)
            f.close()
            print("OK.")
        except Exception as e:
            print("QQ:",e)
        

    def get(url,file):
        try:
            response = get('https://marty5499.github.io/pythonCode/'+url)
            print(">>",len(response.text) )
            print("get file:",file,'size:',len(response.text),',save to:',file)
            f = open(file, 'w')
            f.write(response.text)
            f.close()
            print("OK.")
        except Exception as e:
            print("QQ:",e)


    def exe(dir):
        srcDir = dir
        try:
            while True:
                idx = dir.index('/')
                try:
                    name = dir[0:idx]
                    try:
                        print('mkdir',name)
                        os.mkdir(name)
                    except:
                        pass
                    try:
                        os.chdir(name)
                        print('cd',name)
                    except:
                        pass
                except:
                    pass
                dir = dir[idx+1:]
        except:
            pos = -1
            try:
                pos = dir.index('.mpy')
            except:
                pass
            try:
                if pos == -1:
                    pos = dir.index('.py')
            except:
                pass
            try:
                if pos > 0:
                    pyFile = dir
                    Res.get(srcDir,pyFile)
                else:
                    try:
                        print("mkdir",dir)
                        os.mkdir(dir)
                    except:
                        pass
                    try:
                        os.chdir(dir)
                        print("cd ",dir)
                    except:
                        pass
            except:
                pass
        os.chdir('/')



print("connect...")
do_connect()
print("get files...")
### lib's single file max size: 8256 Bytes (ESP01)
Res.exe('lib/utils.py')
Res.exe('lib/webduino.py')
Res.exe('lib/urequests.py')
Res.exe('lib/WebServer.py')
Res.exe('lib/umqtt/simple.py')

print("========")
print('Mac address:',ubinascii.hexlify(network.WLAN().config('mac'),':').decode())
