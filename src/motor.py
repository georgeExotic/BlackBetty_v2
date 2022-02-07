##MODBUS##
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils

from ast import literal_eval #from hex to dec
import threading

from time import sleep

class Motor:
    def __init__(self):

        self.SERVER_HOST = "192.168.33.1"
        self.SERVER_PORT = 502  

        ###Velocities###
            #Jogging
        self.joggingInitialVelocity = 1000
        self.joggingMaxVelocity = 10000
            #homing
        self.homingInitialVelocity = 10000
        self.homingMaxVelocity = 40000

        ###accelerations###
            #jogging
        self.joggingAcceleration = 50000
        self.joggingDeacceleration = 500000
            #homing
        self.homingAcceleration = 5000000
        self.homingDeacceleration = 5000000

        ###hardware Settings
        self.strokeLength = 30 # mm
        self.pistonDiameter = 19.05 #mm
        self.pistonRadius = self.pistonDiameter/2
        self.leadTravel = 4.000 #mm per rev
        self.stepPerRevolution = 200.000 * 256.000   #200*256 = 51200 steps per rev


        self.lock = threading.Lock()
        self._connectModbusClient()
        self._checkConnection()
        self.setHMT()
        self.setPerformanceFeatures()
        self.setEnable(1)
        self.setProfiles()


    def _connectModbusClient(self):
        #define mosbus server and host
        self._motor = ModbusClient(host = self.SERVER_HOST, port = self.SERVER_PORT, unit_id=1, auto_open=True, debug = False)
        self._motor.open()
        if self._motor.is_open():
            print("connected to " + self.SERVER_HOST + ":" + str(self.SERVER_PORT))
        else:
            print("unable to connect to "+self.SERVER_HOST+ ":" +str(self.SERVER_PORT))
        return

    ###function to check is modbus tcp connection is successful
    def _checkConnection(self):
        if not self._motor.is_open():
            if not self._motor.open():
                self.connectionStatus = 0
                self._connectModbusClient()
                return "unable to connect" #print("unable to connect to motor")
        self.connectionStatus = 1
        return self.connectionStatus

    def _hex2dec(self,hex):
        hex = str(hex)
        dec = int(literal_eval(hex))
        return dec

    def _mm2micron(self,mmValue):
        micronValue = mmValue * 1000
        return micronValue

    def _micron2mm(self,micronValue):
        mmValue = micronValue / 1000
        return mmValue

    def _mm2steps(self, displacment_mm):
        targetRevolutions = displacment_mm/self.leadTravel
        steps = int(targetRevolutions * self.stepPerRevolution)
        return steps

    def _steps2mm(self,steps):
        revs = float(steps/self.stepPerRevolution)
        displacement = float(revs * self.leadTravel)
        return displacement

    ###function to read from register of LMD57 modbus register map
    def _readHoldingRegs(self,startingAddressHex,regSize = 1):
        with self.lock:
            self._checkConnection()
            startingAddressDEC = self._hex2dec(startingAddressHex)
            reading = " "
            try:
                if regSize > 1 :
                    regSize = 2 #registers are 2 or 1 bytes
                    reg = self._motor.read_holding_registers(startingAddressDEC,regSize)
                    if reg is not None:
                        ans = utils.word_list_to_long(reg,False)
                        complement = utils.get_list_2comp(ans,32)
                        reading = complement[0]
                    else:
                        # print(f"Motor Reading {reg} as output 1")
                        reading = 0 # TEMP
                else:
                    regSize = 1
                    reg = self._motor.read_holding_registers(startingAddressDEC,regSize)
                    if reg is not None:
                        reading = reg[0]
                    else:
                        # print(f"Motor Reading {reg} as output 2")
                        pass
            except:
                self._connectModbusClient()
                print("ERROR - readHoldingRegs")
        return reading

    ###function to write to any register of LMD57 modbus register map
    def _writeHoldingRegs(self,startingAddressHEX,regSize,value):
        with self.lock:
            self._checkConnection()
            startingAddressDEC = self._hex2dec(startingAddressHEX)
            try:
                if regSize > 2:
                    complement = utils.get_2comp(value, 32)
                    word = utils.long_list_to_word([complement],False)
                    self._motor.write_multiple_registers(startingAddressDEC,word)
                else:
                    self._motor.write_multiple_registers(startingAddressDEC,[value])
            except:
                self._connectModbusClient()
                # print("ERROR Modbus Reconnected.")
        return

    def setHMT(self):
        hmt = 2
        runCurrent = 100 #0x67
        makeUp = 2       #0xA0
        self._writeHoldingRegs(0x8E,1,hmt)          #set hmt
        self._writeHoldingRegs(0x67,1,runCurrent)   #set run current
        self._writeHoldingRegs(0xA0,1,makeUp)       #set makup frequency

    def setPerformanceFeatures(self):
        holdingCurrent = 100
        controlBound = 0 
        microStep = 256.000  
        self._writeHoldingRegs(0x29,1,holdingCurrent)
        self._writeHoldingRegs(0x91,1,controlBound)
        self._writeHoldingRegs(0x48,1,microStep)

    def setEnable(self,enable):
        self.enable = enable
        self._writeHoldingRegs(0x1C, 1, enable)

    def setProfiles(self,motion = "jogging"):
        if motion == "homing":
            self._writeHoldingRegs(0x89,4,self.homingInitialVelocity)
            self._writeHoldingRegs(0x8B,4,self.homingMaxVelocity)
            self._writeHoldingRegs(0x00,4,self.homingAcceleration)
            self._writeHoldingRegs(0x18,4,self.homingDeacceleration)
        elif motion == "jogging":
            self._writeHoldingRegs(0x89,4,self.joggingInitialVelocity)
            self._writeHoldingRegs(0x8B,4,self.joggingMaxVelocity)
            self._writeHoldingRegs(0x00,4,self.joggingAcceleration)
            self._writeHoldingRegs(0x18,4,self.joggingDeacceleration)

    def move(self,displacement,profile="jogging"):
        self.setProfiles(profile)
        steps2move = self._mm2steps(displacement)
        self._writeHoldingRegs(0x46,4,steps2move)
        print("MOVE COMMAND SENT")

    def stop(self):
        self._writeHoldingRegs(0x46,4,1) # 1 step
        print("STOP COMMAND SENT")

    def updatePosition(self):
        try:
            pos = self._readHoldingRegs(0x57,4)
            position_reading = self._steps2mm(pos)
            self.absolutePosition = position_reading
        except:
            print("ERROR READING POSITION")
            position_reading = 0

        return position_reading

if __name__ == "__main__":
    Motor = Motor()
    Motor.move(5)
    # Motor._stop()
    while True:
        sleep(0.2)
        print(Motor.updatePosition())

