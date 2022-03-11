class debug:
    state = True
    def on():
        debug.state = True
    def off():
        debug.state = False
    def print(msg="",msg2="",msg3=""):
        if debug.state:
            print(msg,msg2) 
