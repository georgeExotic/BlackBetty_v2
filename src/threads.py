from time import sleep
import random
import csv
from PyQt5.QtCore import QThread, pyqtSignal

from motor import Motor
from LoadCell import LoadCell
from limitSwitch import limitSwitch


class LoadCellThread(QThread):

    loadCellReadingSignal = pyqtSignal(float)

    def __init__(self):
        QThread.__init__(self)
        self._connectLoadCell()


    def _connectLoadCell(self):
        self.LoadCell = LoadCell()
        self.LoadCell.connectLoadCell()
        self.LoadCell.loadCalibrationFile()

    def run(self):
        while True:
            self.loadCellReading = self.LoadCell.readForce()
            # self.loadCellReading = random.randint(0,50000)
            self.loadCellReadingSignal.emit(self.loadCellReading)
            sleep(0.1)


class MotorThread(QThread):

    motorPositionReadingSignal = pyqtSignal(float)

    def __init__(self):
        QThread.__init__(self)
        self._connectMotor()

    def _connectMotor(self):
        self.Motor = Motor()

    def run(self):
        while True:
            self.motorPositionReading = self.Motor.updatePosition()
            # self.motorPositionReading = random.randint(0,30000)
            self.motorPositionReadingSignal.emit(self.motorPositionReading)
            sleep(0.1)


class homeThread(QThread):

    def __init__(self,limitSwitchThread,MotorThread):
        QThread.__init__(self)
        self.limitSwitchThread = limitSwitchThread
        self.MotorThread = MotorThread

    def run(self):
        if self.limitSwitchThread.isTop == True:
            self.MotorThread.Motor.home()
        elif self.limitSwitchThread.isTop == False:
            self.MotorThread.Motor.move(40000)
       
            while self.MotorThread.Motor.isMoving() == True:
                if self.limitSwitchThread.isTop == True:
                    self.MotorThread.Motor.stop()
                    sleep(0.1)
                    self.MotorThread.Motor.home()
                    break   

class jogUpThread(QThread):

    def __init__(self,distance2JugUp_MICRON,MotorThread,limitSwitchThread,JUG_UP_BUTTON,JOG_DOWN_BUTTON):
        QThread.__init__(self)
        self.distance2JugUp_MICRON = distance2JugUp_MICRON
        self.MotorThread = MotorThread
        self.limitSwitchThread = limitSwitchThread
        self.JUG_UP_BUTTON = JUG_UP_BUTTON
        self.JOG_DOWN_BUTTON = JOG_DOWN_BUTTON
        
    def run(self):
        self.JUG_UP_BUTTON.setEnabled(False)
        self.JOG_DOWN_BUTTON.setEnabled(False)

        if self.limitSwitchThread.isTop == True:
            pass
        elif self.limitSwitchThread.isTop == False:
            self.MotorThread.Motor.move(int(self.distance2JugUp_MICRON))

            while self.MotorThread.Motor.isMoving() == True:
                if self.limitSwitchThread.isTop == True:
                    self.MotorThread.Motor.stop()
                    break
        self.JUG_UP_BUTTON.setEnabled(True)
        self.JOG_DOWN_BUTTON.setEnabled(True)

class jogDownThread(QThread):

    def __init__(self,distance2JugDown_MICRON,MotorThread,limitSwitchThread,JOG_DOWN_BUTTON,JUG_UP_BUTTON):
        QThread.__init__(self)
        self.distance2JugDown_MICRON = distance2JugDown_MICRON
        self.MotorThread = MotorThread
        self.limitSwitchThread = limitSwitchThread
        self.JOG_DOWN_BUTTON = JOG_DOWN_BUTTON
        self.JUG_UP_BUTTON = JUG_UP_BUTTON
    def run(self):
        self.JOG_DOWN_BUTTON.setEnabled(False)
        self.JUG_UP_BUTTON.setEnabled(False)

        if self.limitSwitchThread.isBottom == True:
            pass
        elif self.limitSwitchThread.isBottom == False:
            self.MotorThread.Motor.move(-1*int(self.distance2JugDown_MICRON))

            while self.MotorThread.Motor.isMoving() == True:
                if self.limitSwitchThread.isBottom == True:
                    self.MotorThread.Motor.stop()
                    break
        self.JOG_DOWN_BUTTON.setEnabled(True)
        self.JUG_UP_BUTTON.setEnabled(True)

class limitSwitchThread(QThread):

    topLimitIndicatorSignal = pyqtSignal(bool)
    bottomLimitIndicatorSignal = pyqtSignal(bool)

    def __init__(self):
        QThread.__init__(self)
        self.topLimit = limitSwitch(5)
        self.bottomLimit = limitSwitch(6)
        self.isTop = False
        self.isBottom = False 


    def checkLimits(self):
        if self.topLimit.getSwitchStatus() == True:
            self.isTop = True
            self.topLimitIndicatorSignal.emit(True)
        elif self.topLimit.getSwitchStatus() == False:
            self.isTop = False
            self.topLimitIndicatorSignal.emit(False)

        if self.bottomLimit.getSwitchStatus() == True:
            self.isBottom = True
            self.bottomLimitIndicatorSignal.emit(True)
        elif self.bottomLimit.getSwitchStatus() == False:
            self.isBottom = False
            self.bottomLimitIndicatorSignal.emit(False)

    def run(self):
        while True:
            self.checkLimits()
            sleep(0.1)

class dataRecordingThread(QThread):

    def __init__(self,MotorThread,LoadCellThread,TOGGLE_DATA_RECORDING_BUTTON):
        QThread.__init__(self)
        self.MotorThread = MotorThread
        self.MotorThread.motorPositionReadingSignal.connect(self.updatePositionReading)
        self.LoadCellThread = LoadCellThread
        self.LoadCellThread.loadCellReadingSignal.connect(self.updateLoadCellReading)
        self.TOGGLE_DATA_RECORDING_BUTTON = TOGGLE_DATA_RECORDING_BUTTON

        self.positionReading_micron = 0
        self.updateLoadCellReading = 0
        

    def updatePositionReading(self,positionReading):
        self.positionReading_micron = positionReading

    def updateLoadCellReading(self,loadCellReading):
        self.updateLoadCellReading = loadCellReading

    def openFile(self,filename):
        try:
            self.filename = filename
            self.csvFile = open(self.filename, 'w')
            self.csvFileWriter = csv.writer(self.csvFile)
            self.csvFileWriter.writerow(['SAMPLE NUMBER','POSITION','LOAD'])#units?
        except:
            return False
        return True

    def closeFile(self):
        try:
            self.csvFile.close()
        except:
            return False
        return True

    def run(self):
        i=0
        if self.openFile('/home/pi/Desktop/BLACKBETTY RESULTS/csvTest.csv'):
            while i<10:
                self.csvFileWriter.writerow([i,self.positionReading_micron,self.updateLoadCellReading])
                i+=1
                sleep(0.1)
        self.closeFile()
        self.TOGGLE_DATA_RECORDING_BUTTON.toggle()
        print("done")