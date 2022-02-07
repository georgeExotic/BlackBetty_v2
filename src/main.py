import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtGui import QPalette 

from motor import Motor
from LoadCell import LoadCell

class App(QtWidgets.QMainWindow):
    def __init__(self, parent=None):

        super(App, self).__init__(parent)
        uic.loadUi('/home/pi/BlackBetty_v2/GUI/blackBettyGUI.ui', self)
        self.resize(1024,600)

        self._connectMotor()
        self._startTHREADS()
        self._connectLoadCell()


        ###BUTTONS###
        self.STOP_MOTOR_BUTTON.clicked.connect(self.STOP_MOTOR)
        self.HOME_BUTTON.clicked.connect(self.HOME)
        self.JUG_UP_BUTTON.clicked.connect(self.JOG_UP)
        self.JOG_DOWN_BUTTON.clicked.connect(self.JOG_DOWN)
        self.TOGGLE_DATA_RECORDING_BUTTON.clicked.connect(self.TOGGLE_DATA_RECORDING)
        self.EXPORT_DATA_BUTTON.clicked.connect(self.EXPORT_DATA)
        self.LOAD_CELL_CALIBRATION_BUTTON.clicked.connect(self.LOAD_CELL_CALIBRATION)

    def _connectMotor(self):
        self.Motor = Motor()

    def _startTHREADS(self):
        pass
    
    def _connectLoadCell(self):
        self.LoadCell = LoadCell()

    ###BUTTON FUNCTIONS###
    def STOP_MOTOR(self):
        pass
    def HOME(self):
        pass
    def JOG_UP(self):
        pass
    def JOG_DOWN(self):
        pass
    def TOGGLE_DATA_RECORDING(self):
        pass
    def EXPORT_DATA(self):
        pass
    def LOAD_CELL_CALIBRATION(self):
        pass

def main():
    app = QApplication(sys.argv)
    form = App()
    form.show()
    app.exec()

if __name__=="__main__":
    main()