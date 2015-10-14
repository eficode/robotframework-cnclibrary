class FakeDevice(object):
    """ class that simulates a serial connected device that understands few gcodes """
    def __init__(self):
        self.home = None
        self.position = None
        self.line = None
        self.connected = True
    def write(self, text):
        # if text.endswith("\r\n\r\n"):
        #     self.connected = True
        self.line = text
        if text.startswith("?"):
            self.line = "MPos:"+str(self.position[0])+","+str(self.position[1])+","+str(self.position[2])
        elif text.startswith("G92"):
            command = text.replace("X","").replace("Y","").replace("Z","").split()
            self.home = [command[1], command[2], command[3]]
            self.position = list(self.home)
        elif text.startswith("G01"):
            # update current position
            command = text.replace("F","").replace("X","").replace("Y","").replace("Z","").split()
            if len(command) >= 4: # xy move
                self.position[0] = float(self.home[0])+float(command[2])
                self.position[1] = float(self.home[1])+float(command[3])
            if len(command) >= 5: # xyz move
                self.position[2] = float(self.home[2])+float(command[4])
            if len(command) == 3: # zmove
                self.position[2] = float(self.home[2])+float(command[2])
        # loopback
   
    def flushInput(self):
        pass
    def close(self):
        self.connected = False
    def readline(self):
        return self.line

class FakeDeviceException:
    pass