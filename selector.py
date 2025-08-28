# selector.py
import sys, json
from PyQt5 import QtWidgets, QtGui, QtCore

class Selector(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Selecteer gebied - sleep met de muis en druk op Enter")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.screen = QtWidgets.QApplication.primaryScreen()
        geom = self.screen.geometry()
        self.setGeometry(geom)
        self.setWindowOpacity(0.35)
        self.start = None
        self.end = None
        self.rects = []
        self.showFullScreen()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('red'), 2))
        if self.start and self.end:
            r = QtCore.QRect(self.start, self.end)
            qp.drawRect(r.normalized())

    def mousePressEvent(self, event):
        self.start = event.pos()
        self.end = self.start
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            r = QtCore.QRect(self.start, self.end).normalized()
            box = {"left": r.left(), "top": r.top(), "width": r.width(), "height": r.height()}
            with open("box.json", "w") as f:
                json.dump(box, f)
            QtWidgets.QApplication.quit()
        elif event.key() == QtCore.Qt.Key_Escape:
            QtWidgets.QApplication.quit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    s = Selector()
    s.show()
    sys.exit(app.exec_())
