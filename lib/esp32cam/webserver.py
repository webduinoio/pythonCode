import gc
import machine
import json
import time
import camera

from microWebSrv import MicroWebSrv

class webcam():

    def __init__(self,port=8080,webPath='/'):
        
        self.saturation = 0
        self.quality = 10
        self.brightness = 0
        self.contrast = 0
        self.vflip = 0
        self.hflip = 0
        self.framesize = camera.FRAME_VGA
        self.port = port
        self.webPath = webPath
        self.routeHandlers = [
            ("/", "GET", self._httpHandlerIndex),
            ("/logo.svg", "GET", self._httpLogo),
            ("/stream/<framesize>", "GET", self._httpStream),
            ("/upy/<saturation>/<brightness>/<contrast>/<quality>/<vflip>/<hflip>/<framesize>", "GET", self._httpHandlerSetData),
            ("/upy", "GET", self._httpHandlerGetData),
            ("/memory/<query>", "GET", self._httpHandlerMemory)
        ]

    def run(self):
        self.led = machine.Pin(4, machine.Pin.OUT)
        try:
            camera.init(0, format=camera.JPEG, framesize=self.framesize)      #ESP32-CAM
        except:
            pass
        mws = MicroWebSrv(routeHandlers=self.routeHandlers, webPath=self.webPath,port=self.port)
        mws.Start(threaded=True)
        gc.collect()

    def _httpStream(self, httpClient, httpResponse, routeArgs):
        print("routeArgs:",routeArgs)
        self.framesize = int(routeArgs['framesize'])
        camera.framesize(self.framesize)
        image = camera.capture()

        headers = { 'Last-Modified' : 'Fri, 1 Jan 2018 23:42:00 GMT', \
                    'Cache-Control' : 'no-cache, no-store, must-revalidate' }

        httpResponse.WriteResponse(code=200, headers=headers,
                                    contentType="image/jpeg",
                                    contentCharset="UTF-8",
                                    content=image)


    def _httpLogo(self, httpClient, httpResponse):
        f = open("www/logo.svg", "r")
        content =  f.read()
        f.close()

        httpResponse.WriteResponseOk(headers=None,
                                    contentType="image/svg+xml",
                                    contentCharset="UTF-8",
                                    content=content)


    def _httpHandlerIndex(self, httpClient, httpResponse):
        f = open("index.html", "r")
        content =  f.read()
        f.close()

        headers = { 'Last-Modified' : 'Fri, 1 Jan 2018 23:42:00 GMT', \
                            'Cache-Control' : 'no-cache, no-store, must-revalidate' }

        httpResponse.WriteResponseOk(headers=None,
                                    contentType="text/html",
                                    contentCharset="UTF-8",
                                    content=content)

    def _httpHandlerSetData(self, httpClient, httpResponse, routeArgs):
        self.saturation = int(routeArgs['saturation']) - 2
        self.brightness = int(routeArgs['brightness']) - 2 
        self.contrast = int(routeArgs['contrast']) - 2
        self.quality = int(routeArgs['quality'])
        self.vflip = bool(routeArgs['vflip'])
        self.hflip = bool(routeArgs['hflip'])
        self.framesize = int(routeArgs['framesize'])

        camera.saturation(self.saturation)
        camera.brightness(self.brightness)
        camera.contrast(self.contrast)
        camera.quality(self.quality)
        camera.flip(self.vflip)
        camera.mirror(self.hflip)
        camera.framesize(self.framesize)

        data = {
            'saturation': self.saturation,
            'brightness': self.brightness,
            'contrast': self.contrast,
            'quality': self.quality,
            'vflip': self.vflip,
            'hflip': self.hflip,
            'framesize': self.framesize
        }
        self._newdata = True
        httpResponse.WriteResponseOk(headers=None,
                                        contentType="text/html",
                                        contentCharset="UTF-8",
                                        content=json.dumps(data))

    def _httpHandlerGetData(self, httpClient, httpResponse):
        data = {
            'saturation': self.saturation,
            'brightness': self.brightness,
            'contrast': self.contrast,
            'quality': self.quality,
            'vflip': self.vflip,
            'hflip': self.hflip,
            'framesize': self.framesize
        }

        httpResponse.WriteResponseOk(headers=None,
                                    contentType="application/json",
                                    contentCharset="UTF-8",
                                    content=json.dumps(data))

    def _httpHandlerMemory(self, httpClient, httpResponse, routeArgs):
        print("In Memory HTTP variable route :")
        query = str(routeArgs['query'])

        if 'gc' in query or 'collect' in query:
            gc.collect()

        content = """\
            {}
            """.format(gc.mem_free())
        httpResponse.WriteResponseOk(headers=None,
                                    contentType="text/html",
                                    contentCharset="UTF-8",
                                    content=content)
