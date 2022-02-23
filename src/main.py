import sys
import math
import csv
from time import sleep
from xmlrpc.client import boolean
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtGui import QPalette 

from motor import Motor
from LoadCell import LoadCell
from limitSwitch import limitSwitch

class App(QtWidgets.QMainWindow):
    def __init__(self, parent=None):

        super(App, self).__init__(parent)
        self.gui = uic.loadUi('/home/pi/BlackBetty_v2/GUI/blackBettyGUI.ui', self)
        self.resize(1024,600)
        self._startTHREADS()
        self.firstLoop = True
        
        ###BUTTONS###
        self.STOP_MOTOR_BUTTON.clicked.connect(self.STOP_MOTOR)
        self.HOME_BUTTON.clicked.connect(self.HOME)
        self.JUG_UP_BUTTON.clicked.connect(self.JOG_UP)
        self.JOG_DOWN_BUTTON.clicked.connect(self.JOG_DOWN)
        self.TOGGLE_DATA_RECORDING_BUTTON.clicked.connect(self.TOGGLE_DATA_RECORDING)
        self.LOAD_CELL_CALIBRATION_BUTTON.clicked.connect(self.LOAD_CELL_CALIBRATION)

        self.turnOffButtons()

    def _startTHREADS(self):
        ##PUT THREADS HERE##
        self.LoadCellThread = LoadCellThread()
        self.LoadCellThread.start()
        self.LoadCellThread.loadCellReadingSignal.connect(self.updateLoadCellValue)

        self.MotorThread = MotorThread()
        self.MotorThread.start()
        self.MotorThread.motorPositionReadingSignal.connect(self.updatePositionReading)

        self.limitSwitchThread = limitSwitchThread()
        self.limitSwitchThread.start()
        self.limitSwitchThread.topLimitIndicatorSignal.connect(self.updateColorTop)
        self.limitSwitchThread.bottomLimitIndicatorSignal.connect(self.updateColorBottom)

    ###BUTTON FUNCTIONS###
    def STOP_MOTOR(self):
        self.MotorThread.Motor.stop()
        self.JUG_UP_BUTTON.setEnabled(True)
        self.JOG_DOWN_BUTTON.setEnabled(True)


    def HOME(self):
        self.homeThread = homeThread(self.limitSwitchThread,self.MotorThread)
        self.homeThread.start()
        self.turnOnButtons()


    def JOG_UP(self):
        distance2JugUp_MICRON = self.JOG_UP_INPUT_MICRON.text()
        self.jogUpThread = jogUpThread(distance2JugUp_MICRON,self.MotorThread,self.limitSwitchThread,self.JUG_UP_BUTTON,self.JOG_DOWN_BUTTON)
        self.jogUpThread.start()

    def JOG_DOWN(self):
        distance2JugDown_MICRON = self.JOG_DOWN_INPUT_MICRON.text()
        self.jogDownThread = jogDownThread(distance2JugDown_MICRON,self.MotorThread,self.limitSwitchThread,self.JOG_DOWN_BUTTON,self.JUG_UP_BUTTON)
        self.jogDownThread.start()

    def TOGGLE_DATA_RECORDING(self):
        self.dataRecordingThread = dataRecordingThread(self.MotorThread,self.LoadCellThread,self.TOGGLE_DATA_RECORDING_BUTTON)
        if self.TOGGLE_DATA_RECORDING_BUTTON.isChecked():
            self.dataRecordingThread.start()
        # elif not self.TOGGLE_DATA_RECORDING_BUTTON.isChecked():
        #     self.dataRecordingThread.stop()

    def LOAD_CELL_CALIBRATION(self):

        pass


    def turnOnButtons(self):

        self.JUG_UP_BUTTON.setEnabled(True)
        self.JOG_DOWN_BUTTON.setEnabled(True)
        self.TOGGLE_DATA_RECORDING_BUTTON.setEnabled(True)
        self.LOAD_CELL_CALIBRATION_BUTTON.setEnabled(True)
        self.STOP_MOTOR_BUTTON.setEnabled(True)
        self.HOME_BUTTON.setEnabled(True)
    
    def turnOffButtons(self):
        
        if not self.firstLoop:
            self.HOME_BUTTON.setEnabled(False)
        self.JUG_UP_BUTTON.setEnabled(False)
        self.JOG_DOWN_BUTTON.setEnabled(False)
        self.TOGGLE_DATA_RECORDING_BUTTON.setEnabled(False)
        self.LOAD_CELL_CALIBRATION_BUTTON.setEnabled(False)
        self.STOP_MOTOR_BUTTON.setEnabled(False)
        
        self.firstLoop = False


    ##WORKERS##
    def updateLoadCellValue(self,loadCellValue_KG):
        loadCellValue_KG = round(loadCellValue_KG,3)
        value_N = round(loadCellValue_KG * 9.8,3)
        ###pressure###
        pistonDiameter = 19.05
        pistonRadius = pistonDiameter/2
        pistonradius_meters = pistonRadius/1000
        pistonArea = math.pi*math.pow(pistonradius_meters,2)
        pressureReading_KPA = round(((value_N)/(pistonArea)/1000),3)

        self.FORCE_READING_KG.display(loadCellValue_KG)
        self.FORCE_READING_N.display(value_N)
        self.PRESSURE_READING_PA.display(pressureReading_KPA)
    
    def updatePositionReading(self,positionReading):
        self.positionReading_mm = round(positionReading,6)
        self.positionReading_micron = self.positionReading_mm * 1000
        self.POSITION_MM.display(self.positionReading_mm)
        self.POSITION_MICRON.display(self.positionReading_micron)

    
    def updateColorBottom(self,state):
        if state:
            self.bottomLimitIndicator.setStyleSheet("background-color: rgb(0, 255, 0);")
        else:
            self.bottomLimitIndicator.setStyleSheet("background-color: rgb(255, 0, 0);")
            
    def updateColorTop(self,state):
        if state:
            self.topLimitIndicator.setStyleSheet("background-color: rgb(0, 255, 0);")
        else:
            self.topLimitIndicator.setStyleSheet("background-color: rgb(255, 0, 0);")


class LoadCellThread(QThread):

    loadCellReadingSignal = QtCore.pyqtSignal(float)

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
            self.loadCellReadingSignal.emit(self.loadCellReading)
            sleep(0.1)
    def stop(self):
        self.terminate()

class MotorThread(QThread):

    motorPositionReadingSignal = QtCore.pyqtSignal(float)

    def __init__(self):
        QThread.__init__(self)
        self._connectMotor()

    def _connectMotor(self):
        self.Motor = Motor()

    def run(self):
        while True:
            self.motorPositionReading = self.Motor.updatePosition()
            self.motorPositionReadingSignal.emit(self.motorPositionReading)
            sleep(0.1)

    def stop(self):
        self.terminate()

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

    topLimitIndicatorSignal = QtCore.pyqtSignal(bool)
    bottomLimitIndicatorSignal = QtCore.pyqtSignal(bool)

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
        self.LoadCellThread = LoadCellThread
        self.TOGGLE_DATA_RECORDING_BUTTON = TOGGLE_DATA_RECORDING_BUTTON

        filePath = '/home/pi/Desktop/csvTest.csv'
        self.csvFile = open(filePath,'w')
        self.csvFileWriter = csv.writer(self.csvFile)



    def run(self):
        i=1
        # with open(filePath,'w') as self.csvFile:
        #     csvFileWriter = csv.writer(self.csvFile)
        self.csvFileWriter.writerow(['i','POSITION','LOAD'])
        while self.TOGGLE_DATA_RECORDING_BUTTON.isChecked():
            self.csvFileWriter.writerow([i,self.MotorThread.motorPositionReading,self.LoadCellThread.loadCellReading])
            i+=1
            sleep(0.1)



def main():
    app = QApplication(sys.argv)
    form = App()
    form.show()
    app.exec()

if __name__=="__main__":
    main()