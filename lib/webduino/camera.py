import time, machine, camera, ubinascii, gc

class Camera():
    
    def init():
        try:
            Camera.initState
        except:
            Camera.initState = 0
        if Camera.initState is not 1:
            try:
                camera.init(0, format=camera.JPEG,xclk_freq=camera.XCLK_20MHz)
                camera.framesize(15)
                camera.quality(10)
                camera.framesize(camera.FRAME_UXGA)
                time.sleep(0.1)
                Camera.initState = 1
            except:
                print("Camera exception !!!")
                Camera.initState = -1
                machine.reset()
                pass
            
    def snapshot():
        jpg = camera.capture()
        image = ubinascii.b2a_base64(jpg)
        del jpg
        time.sleep(0.1)
        gc.collect()
        return image
