import sys
import math
from time import sleep
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets, uic
from threads import (LoadCellThread,
                    MotorThread,
                    homeThread,
                    jogUpThread,
                    jogDownThread,
                    dataRecordingThread)


class App(QtWidgets.QMainWindow):
    def __init__(self, parent=None):

        super(App, self).__init__(parent)
        self.gui = uic.loadUi('../GUI/blackBettyGUI.ui', self)
        self.resize(1024,600)
        self._startTHREADS()
        self.firstLoop = True
        
        ###BUTTONS###
        # self.STOP_MOTOR_BUTTON.clicked.connect(self.STOP_MOTOR)
        # self.HOME_BUTTON.clicked.connect(self.HOME)
        # self.JUG_UP_BUTTON.clicked.connect(self.JOG_UP)
        # self.JOG_DOWN_BUTTON.clicked.connect(self.JOG_DOWN)
        self.TOGGLE_DATA_RECORDING_BUTTON.clicked.connect(self.TOGGLE_DATA_RECORDING)
        # self.LOAD_CELL_CALIBRATION_BUTTON.clicked.connect(self.LOAD_CELL_CALIBRATION)

        # self.turnOffButtons()

    def _startTHREADS(self):
        ##PUT THREADS HERE##
        self.LoadCellThread = LoadCellThread()
        self.LoadCellThread.start()
        self.LoadCellThread.loadCellReadingSignal.connect(self.updateLoadCellValue)

        self.MotorThread = MotorThread()
        self.MotorThread.start()
        self.MotorThread.motorPositionReadingSignal.connect(self.updatePositionReading)

        # self.limitSwitchThread = limitSwitchThread()
        # self.limitSwitchThread.start()
        # self.limitSwitchThread.topLimitIndicatorSignal.connect(self.updateColorTop)
        # self.limitSwitchThread.bottomLimitIndicatorSignal.connect(self.updateColorBottom)


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
        self.TOGGLE_DATA_RECORDING_BUTTON.setEnabled(True)
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






def main():
    app = QApplication(sys.argv)
    form = App()
    form.show()
    app.exec()

if __name__=="__main__":
    main()