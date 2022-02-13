import sys
import math
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
        uic.loadUi('/home/pi/BlackBetty_v2/GUI/blackBettyGUI.ui', self)
        self.resize(1024,600)

        self._startTHREADS()

        
        ###BUTTONS###
        self.STOP_MOTOR_BUTTON.clicked.connect(self.STOP_MOTOR)
        self.HOME_BUTTON.clicked.connect(self.HOME)
        self.JUG_UP_BUTTON.clicked.connect(self.JOG_UP)
        self.JOG_DOWN_BUTTON.clicked.connect(self.JOG_DOWN)
        self.TOGGLE_DATA_RECORDING_BUTTON.clicked.connect(self.TOGGLE_DATA_RECORDING)
        self.EXPORT_DATA_BUTTON.clicked.connect(self.EXPORT_DATA)
        self.LOAD_CELL_CALIBRATION_BUTTON.clicked.connect(self.LOAD_CELL_CALIBRATION)

        # self.STOP_MOTOR_BUTTON.setEnabled(False)
        # self.JUG_UP_BUTTON.setEnabled(False)
        # self.JOG_DOWN_BUTTON.setEnabled(False)
        # self.TOGGLE_DATA_RECORDING_BUTTON.setEnabled(False)
        # self.EXPORT_DATA_BUTTON.setEnabled(False)
        # self.LOAD_CELL_CALIBRATION_BUTTON.setEnabled(False)


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


    ###BUTTON FUNCTIONS###
    def STOP_MOTOR(self):
        self.MotorThread.Motor.stop()

    def HOME(self):
        self.MotorThread.Motor.move(40,"homing")
        self.STOP_MOTOR_BUTTON.setEnabled(True)
        self.JUG_UP_BUTTON.setEnabled(True)
        self.JOG_DOWN_BUTTON.setEnabled(True)
        self.TOGGLE_DATA_RECORDING_BUTTON.setEnabled(True)
        self.EXPORT_DATA_BUTTON.setEnabled(True)
        self.LOAD_CELL_CALIBRATION_BUTTON.setEnabled(True)

    def JOG_UP(self):
        distance2JugUp_MICRON = self.JOG_UP_INPUT_MICRON.text()
        self.jogUpThread = jogUpThread(distance2JugUp_MICRON,self.MotorThread,self.limitSwitchThread)
        self.jogUpThread.start()

    def JOG_DOWN(self):
        distance2JugDown_MICRON = self.JOG_DOWN_INPUT_MICRON.text()
        self.jogDownThread = jogDownThread(distance2JugDown_MICRON,self.MotorThread)
        self.jogDownThread.start()

    def TOGGLE_DATA_RECORDING(self):
        pass
    def EXPORT_DATA(self):
        pass
    def LOAD_CELL_CALIBRATION(self):
        pass

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
        self.pistionReading_micron = self.positionReading_mm * 1000
        self.POSITION_MM.display(self.positionReading_mm)
        self.POSITION_MICRON.display(self.pistionReading_micron)

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

class jogUpThread(QThread):

    def __init__(self,distance2JugUp_MICRON,MotorThread,limitSwitchThread):
        QThread.__init__(self)
        self.distance2JugUp_MICRON = distance2JugUp_MICRON
        self.MotorThread = MotorThread
        self.limitSwitchThread = limitSwitchThread
        
    def run(self):
        self.MotorThread.Motor.move(int(self.distance2JugUp_MICRON))
        while True:
            if self.MotorThread.Motor.isMoving():
                print("MOVING")
            else:
                print("NOT MOVING")

            # if self.limitSwitchThread.isTop == True:
            # elif self.limitSwitchThread.isTop == False:


class jogDownThread(QThread):

    def __init__(self,distance2JugDown_MICRON,MotorThread):
        QThread.__init__(self)
        self.distance2JugDown_MICRON = distance2JugDown_MICRON
        self.MotorThread = MotorThread
    def run(self):
        self.MotorThread.Motor.move(-1*int(self.distance2JugDown_MICRON))

class limitSwitchThread(QThread):


    def __init__(self):
        QThread.__init__(self)
        self.topLimit = limitSwitch(5)
        self.bottomLimit = limitSwitch(6)
        self.isTop = False
        self.isBottom = False 

    def checkLimits(self):
        if self.topLimit.getSwitchStatus() == True:
            self.isTop = True
        elif self.topLimit.getSwitchStatus() == False:
            self.isTop = False

        if self.bottomLimit.getSwitchStatus() == True:
            self.isBottom = True
        elif self.bottomLimit.getSwitchStatus() == False:
            self.isBottom = False

    def run(self):
        while True:
            self.checkLimits()
            sleep(0.1)


def main():
    app = QApplication(sys.argv)
    form = App()
    form.show()
    app.exec()

if __name__=="__main__":
    main()