import serial
import time

BASE_WIDTH = 248    # millimeters
MAX_SPEED = 300     # millimeters/second

class xv21(object):
    def __init__(self,port):
        self.connect = serial.Serial(port, 115200)
        self.TestMode('on')
        self.Lidar('on')
        self.stop_state = True
 
    def TestMode(self,flag):
        message = 'TestMode '+ flag + '\n'
        self.connect.write(message.encode())
        data = self.read()

    def Lidar(self,flag):
        message = 'SetLDSRotation ' + flag + '\n'
        self.connect.write(message.encode())
        data = self.read()
     
    def getMotors(self):
        self.connect.write('GetMotors\n'.encode())
        wheel = {}          
        data = self.read()
        data = data.decode().split('\r\n')
        for l in data[2:-1]:
            r = l.split(',')
            name = r[0]
            value = r[1]
            wheel[name] = int(value)

        right = wheel['RightWheel_PositionInMM']
        left  = wheel['LeftWheel_PositionInMM']
        
        return right, left
    
    def getScanRanges(self):
        ranges = list()
        scanvals=[]
        self.connect.write('GetLDSScan\n'.encode())
        scan = self.read().decode().split('\r\n')
        for line in scan[2:-2]:
            try:
                vals = line.split(',')
                # Only use legitimate scan tuples with zero error
                if len(vals) == 4 and not int(vals[3]):
                    angle = int(vals[0])
                    distance = int(vals[1])
                    intensity = int(vals[2])
                    #scanvals.append([angle, distance])
                    ranges.append(distance/1000.0)
                    
            except:
                None
        return ranges
    
    def stop(self):
        self.setMotors(0,0,0)
        self.Lidar('off')
        self.TestMode('off')
        
    
    def setMotors(self, l, r, s):
        """ Set motors, distance left & right + speed """
        
        if (int(l) == 0 and int(r) == 0 and int(s) == 0):
            if (not self.stop_state):
                self.stop_state = True
                l = 1
                r = 1
                s = 1
        else:
            self.stop_state = False
        command = "setmotor "+str(int(l))+" "+str(int(r))+" "+str(int(s))+"\n"
        self.connect.write(command.encode())
        data = self.read()
        
    def read(self):
        line = b''
        while True:
            data = self.connect.read()
            line+=data
            if data==b'\x1a':
                break
        return line

        
if __name__ == '__main__':
    robot = xv21('/dev/ttyACM1')
    while True:
        try:
            encoders = robot.getMotors()
            scan =    robot.getScan()
            robot.setMotors(100,100,100)
            print(encoders)
            print(scan)
        except KeyboardInterrupt:
            robot.stop()
