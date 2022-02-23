import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QFormLayout, QLineEdit




def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('PyQt5 App')
    window.setGeometry(200, 200, 280, 80)
    window.move(60, 15)

    window2 = QWidget(parent=window)
    window2.setWindowTitle('PyQt5 App')
    window2.setGeometry(200, 200, 280, 80)
    window2.move(100, 150)

    layout2 = QFormLayout()
    layout2.addRow('Name:', QLineEdit())
    layout2.addRow('Age:', QLineEdit())
    layout2.addRow('Job:', QLineEdit())
    layout2.addRow('Hobbies:', QLineEdit())
    window2.setLayout(layout2)

    layout = QHBoxLayout()
    layout.addWidget(QLabel('<h2>Hello World!</h2>'))
    layout.addWidget(QLabel('<h2>Hello World!</h2>'))
    layout.addWidget(QLabel('<h2>Hello World!</h2>'))
    window.setLayout(layout)
    window.show()
    window2.show()

    sys.exit(app.exec_())

if __name__=="__main__":
    main()