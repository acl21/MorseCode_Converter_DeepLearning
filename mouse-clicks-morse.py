from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QDesktopWidget, QPushButton, QGridLayout
import sys
from morse_converter import MorseConverter as mc


class MouseClicksMorse(QWidget):

    def __init__(self):
        super().__init__()
        self.inputArea = InputArea()
        self.initUI()

    def initUI(self):
        self.center()
        self.resize(700, 500)
        self.setWindowTitle('Mouse Clicks - Morse Code Conversion')

        self.inputArea.update_labels.connect(self.updateLabels)
        self.inputArea.clear_labels.connect(self.clearLabels)

        inst = QLabel()
        inst.setText('Instructions:\n Dot (.)\t\t:  Left Click\n Dash (-)\t\t:  Double Left Click\n Next Letter\t:  Right Click\n Next Word\t:  Double Right Click')
        font = QtGui.QFont("MoolBoran", 18)
        font.setStyleHint(QtGui.QFont.TypeWriter)
        inst.setFont(font)

        grid = QGridLayout()
        grid.setSpacing(5)
        grid.addWidget(inst, 1, 3)
        grid.addWidget(self.inputArea, 1, 0, 5, 1)
        grid.addWidget(self.inputArea.outputMorse, 3, 3)
        grid.addWidget(self.inputArea.outputConverted, 4, 3)
        grid.addWidget(self.inputArea.clearButton, 5, 3)

        self.setLayout(grid)

        self.setGeometry(300, 300, 550, 300)
        self.setWindowTitle('Mouse Clicks - Morse Code Conversion')

        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def updateLabels(self):
        self.inputArea.outputMorse.setText('Morse Code: <b>' + self.inputArea.message.replace('*', ' ').replace('.', '·'))
        if self.inputArea.message[-1] == '*':
            self.inputArea.outputConverted.setText('Conv. Text: <b>' + mc._morseToText(self.inputArea.message))

    def clearLabels(self):
        self.inputArea.outputMorse.setText('Morse Code: ')
        self.inputArea.outputConverted.setText('Conv. Text: ')
        self.inputArea.message = ''


class InputArea(QWidget):

    update_labels = pyqtSignal()
    clear_labels = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.setInterval(250)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timeout)
        self.click_count = 0
        self.message = ''
        self.temp = ''

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.lightGray)
        self.setPalette(p)

        self.outputMorse = QLabel()
        self.outputMorse.setText('Morse Code: ')
        self.outputConverted = QLabel()
        self.outputConverted.setText('Conv. Text: ')
        font = QtGui.QFont("Consolas", 10)
        font.setStyleHint(QtGui.QFont.TypeWriter)
        self.outputMorse.setFont(font)
        self.outputConverted.setFont(font)

        self.clearButton = QPushButton('Clear All')
        self.clearButton.clicked.connect(self.sendClearSignal)

    def mousePressEvent(self, event):
        self.click_count += 1
        if event.button() == Qt.LeftButton:
            self.temp = '.'
        if event.button() == Qt.RightButton:
            self.temp = '*'
        if not self.timer.isActive():
            self.timer.start()

    def timeout(self):
        if self.click_count > 1:
            if self.temp == '*':
                self.message += '**'
            else:
                self.message += '-'
        else:
            self.message += self.temp
        self.click_count = 0
        self.update_labels.emit()

    def sendClearSignal(self):
        self.clear_labels.emit()

    def getMessage(self):
        return self.message

    def printMessage(self):
        print(self.message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MouseClicksMorse()
    # print(ex.message)
    sys.exit(app.exec_())