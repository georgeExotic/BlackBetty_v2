import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtGui import QPalette 

class App(QtWidgets.QMainWindow):
    def __init__(self, parent=None):

        super(App, self).__init__(parent)
        uic.loadUi('newBlackBetty.ui', self)
        self.resize(1024,600)
        self._connectStepper()
        self._startTHREADS()
        self.JUG_UP_BUTTON.clicked.connect(self.jorge)

    def jorge(self):
        print('jog up')
    def _connectStepper(self):
        
        pass

    def _startTHREADS(self):
        pass


def main():
    app = QApplication(sys.argv)
    form = App()
    form.show()
    app.exec()

if __name__=="__main__":
    main()