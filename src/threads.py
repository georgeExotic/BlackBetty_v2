from time import sleep, time
import math
import datetime
import os.path
import random
import csv
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
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
        pass

    def run(self):
        while True:
            self.loadCellReading = self.LoadCell.read()
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
        pass

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

    def __init__(self,MotorThread, LoadCellThread,
                START_DATA_LOGGING_FILE_BUTTON, TOGGLE_DATA_RECORDING_BUTTON, CLOSE_DATA_LOGGING_FILE_BUTTON,
                fileNameInput, DATA_LOGGING_STATUS, LAYER_NUMBER):

        QThread.__init__(self)
        self.MotorThread = MotorThread
        self.MotorThread.motorPositionReadingSignal.connect(self.updatePositionReading)

        self.LoadCellThread = LoadCellThread
        self.LoadCellThread.loadCellReadingSignal.connect(self.updateLoadCellReading)

        self.START_DATA_LOGGING_FILE_BUTTON = START_DATA_LOGGING_FILE_BUTTON

        self.TOGGLE_DATA_RECORDING_BUTTON = TOGGLE_DATA_RECORDING_BUTTON
        self.TOGGLE_DATA_RECORDING_BUTTON.setEnabled(True)

        self.CLOSE_DATA_LOGGING_FILE_BUTTON = CLOSE_DATA_LOGGING_FILE_BUTTON
        self.CLOSE_DATA_LOGGING_FILE_BUTTON.setEnabled(True)
        self.CLOSE_DATA_LOGGING_FILE_BUTTON.clicked.connect(self.closeDataLogging)

        self.DATA_LOGGING_STATUS = DATA_LOGGING_STATUS
        self.fileNameInput = fileNameInput
        self.LAYER_NUMBER = LAYER_NUMBER


        self.positionReading_micron = 0
        self.updateLoadCellReading = 0
        self.close = False
        self.timeInterval = 0 
        

    def updatePositionReading(self,positionReading_mm):
        self.positionReading_mm = positionReading_mm
        self.positionReading_micron = self.positionReading_mm * 1000

    def updateLoadCellReading(self,loadCellReading_KG):
        self.loadCellValue_KG = round(loadCellReading_KG,3)
        self.loadCellValue_N = round(loadCellReading_KG * 9.8,3)
        ###pressure###
        self.pistonDiameter = 19.05
        self.pistonRadius = self.pistonDiameter/2
        self.pistonradius_meters = self.pistonRadius/1000
        self.pistonArea = math.pi*math.pow(self.pistonradius_meters,2)
        self.pressureReading_KPA = round(((self.loadCellValue_N)/(self.pistonArea)/1000),3)
        self.pressureReading_PA = self.pressureReading_KPA/1000


    def closeDataLogging(self):
        self.close = True
        self.CLOSE_DATA_LOGGING_FILE_BUTTON.setEnabled(False)
        self.TOGGLE_DATA_RECORDING_BUTTON.setEnabled(False)
        self.START_DATA_LOGGING_FILE_BUTTON.setEnabled(True)


    def openFile(self,filename):
        try:
            self.filename = filename                  
            while os.path.exists(self.filename + '.csv'):
                self.filename = self.filename + '_1'
            
            self.csvFile = open(self.filename + '.csv' , 'w')
            self.csvFileWriter = csv.writer(self.csvFile)
            self.csvFileWriter.writerow(['TIMESTAMP','TIME[s]','LAYER NUMBER','FORCE[N]','PRESSURE[KPA]','PRESSURE[PA]','POSITION[Um]','POSITION[mm]'])
        except:
            return False
        return True

    def closeFile(self):
        self.csvFile.close()

    def run(self):
        timeInterval = 0
        if self.openFile('/home/pi/Desktop/BLACKBETTY RESULTS/' + self.fileNameInput):
            
            while not self.close:
                while self.TOGGLE_DATA_RECORDING_BUTTON.isChecked() and self.close == False:
                    self.csvFileWriter.writerow([datetime.datetime.now(),timeInterval,self.LAYER_NUMBER.value(),self.loadCellValue_N,self.pressureReading_KPA,self.pressureReading_PA,self.positionReading_micron,self.positionReading_mm])
                    self.DATA_LOGGING_STATUS.setText('LOGGING')
                    previousTime = time()
                    sleep(0.1)
                    timeInterval = round(timeInterval + (time() - previousTime),2)

                self.DATA_LOGGING_STATUS.setText('NOT LOGGING')
                
        else:
            print("SOMETHING WENT WRONG")

        self.closeFile()
        print("DONE")