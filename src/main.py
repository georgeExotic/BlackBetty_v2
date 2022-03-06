import sys
import math
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets, uic
from threads import (LoadCellThread,
                    MotorThread,
                    homeThread,
                    jogUpThread,
                    jogDownThread,
                    dataRecordingThread)


class App(QMainWindow):
    def __init__(self, parent=None):

        super(App, self).__init__(parent)
        self.gui = uic.loadUi('../GUI/blackBettyGUI.ui', self)
        self.resize(1024,600)
        self._startTHREADS()
        self.turnButtonsOFF()

        ###BUTTONS###
        self.STOP_MOTOR_BUTTON.clicked.connect(self.STOP_MOTOR)
        self.HOME_BUTTON.clicked.connect(self.HOME)
        self.JUG_UP_BUTTON.clicked.connect(self.JOG_UP)
        self.JOG_DOWN_BUTTON.clicked.connect(self.JOG_DOWN)
        self.TOGGLE_DATA_RECORDING_BUTTON.clicked.connect(self.TOGGLE_DATA_RECORDING)

    def turnButtonsOFF(self):
        self.STOP_MOTOR_BUTTON.setEnabled(False)
        self.JUG_UP_BUTTON.setEnabled(False)
        self.JOG_DOWN_BUTTON.setEnabled(False)

    def turnButtonsON(self):
        self.STOP_MOTOR_BUTTON.setEnabled(True)
        self.JUG_UP_BUTTON.setEnabled(True)
        self.JOG_DOWN_BUTTON.setEnabled(True)
        
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


    ###BUTTON FUNCTIONS###
    def STOP_MOTOR(self):
        self.MotorThread.Motor.stop()
        self.JUG_UP_BUTTON.setEnabled(True)
        self.JOG_DOWN_BUTTON.setEnabled(True)

    def HOME(self):
        self.homeThread = homeThread(self.limitSwitchThread,self.MotorThread)
        self.homeThread.start()
        self.turnButtonsON()

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
        
        self.TOPFLAG_INDICATOR.setStyleSheet("background-color:yellow")

        if self.TOGGLE_DATA_RECORDING_BUTTON.isChecked():
            self.dataRecordingThread.start()

    
    def LOAD_CELL_CALIBRATION(self):
        pass


    ###WORKERS###
    def updateLoadCellValue(self,loadCellValue_KG):
        self.loadCellValue_KG = round(loadCellValue_KG,3)
        self.value_N = round(loadCellValue_KG * 9.8,3)
        ###pressure###
        self.pistonDiameter = 19.05
        self.pistonRadius = self.pistonDiameter/2
        self.pistonradius_meters = self.pistonRadius/1000
        self.pistonArea = math.pi*math.pow(self.pistonradius_meters,2)
        self.pressureReading_KPA = round(((self.value_N)/(self.pistonArea)/1000),3)

        self.FORCE_READING_KG.display(self.loadCellValue_KG)
        self.FORCE_READING_N.display(self.value_N)
        self.PRESSURE_READING_PA.display(self.pressureReading_KPA)
    
    def updatePositionReading(self,positionReading):
        self.positionReading_mm = round(positionReading,6)
        self.positionReading_micron = self.positionReading_mm * 1000
        self.POSITION_MM.display(self.positionReading_mm)
        self.POSITION_MICRON.display(self.positionReading_micron)


def main():
    app = QApplication(sys.argv)
    form = App()
    form.show()
    app.exec()

if __name__=="__main__":
    main()