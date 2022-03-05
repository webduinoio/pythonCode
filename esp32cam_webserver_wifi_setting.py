from webduino import Board
 
#####################
try:
    import cmd
    machine.reset()
except:
    pass
#####################

waboard = Board(devId="waboard")
waboard.enableAP()