import sys, os, json
import pytesseract
import cv2
import numpy as np
import mss
from PyQt5 import QtWidgets, QtCore, QtGui

# Zet je Tesseract-pad hier:
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\djvin\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"measurement_type": "Snelheid", "from_unit": "m/s", "to_unit": "km/h"}

def convert_speed(val, frm, to):
    to_mps = {"m/s":1.0,"km/h":1/3.6,"mph":0.44704,"ft/s":0.3048,"kn":0.514444}
    mps = val * to_mps[frm]
    return mps / to_mps[to]

def convert_distance(val, frm, to):
    to_m = {"mm":0.001,"cm":0.01,"m":1.0,"km":1000.0,"inch":0.0254,"ft":0.3048,"yd":0.9144,"mile":1609.344}
    meters = val * to_m[frm]
    return meters / to_m[to]

def convert_temperature(val, frm, to):
    if frm == to: return val
    if frm=="C": c=val
    elif frm=="F": c=(val-32)*5.0/9.0
    elif frm=="K": c=val-273.15
    else: return val
    return c if to=="C" else (c*9.0/5.0+32 if to=="F" else c+273.15)

class Overlay(QtWidgets.QWidget):
    def __init__(self, box):
        super().__init__()
        self.box = box
        self.config = load_config()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | 
                            QtCore.Qt.WindowStaysOnTopHint | 
                            QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(box["left"], box["top"], box["width"], box["height"])
        self.orig_val = "-"
        self.conv_val = "-"
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_ocr)
        self.timer.start(250)
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        font = QtGui.QFont("Segoe UI", 20, QtGui.QFont.Bold)
        qp.setFont(font)

        # Schaduw
        qp.setPen(QtGui.QPen(QtGui.QColor(0,0,0,180), 4))
        qp.drawText(10, 30, f"{self.conv_val} {self.config['to_unit']}")
        qp.drawText(10, 60, f"{self.orig_val} {self.config['from_unit']}")

        # Hoofdtekst
        qp.setPen(QtGui.QColor(255,255,255))
        qp.drawText(10, 30, f"{self.conv_val} {self.config['to_unit']}")
        qp.drawText(10, 60, f"{self.orig_val} {self.config['from_unit']}")

    def update_ocr(self):
        with mss.mss() as sct:
            img = np.array(sct.grab(self.box))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray,(3,3),0)
            _,th = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            config = "--psm 7 -c tessedit_char_whitelist=0123456789.,-"
            text = pytesseract.image_to_string(th, config=config)
            cleaned = "".join(ch for ch in text if ch in "0123456789.,-").replace(",",".")
            try:
                val = float(cleaned)
                self.orig_val = f"{val:.2f}"
                if self.config["measurement_type"]=="Snelheid":
                    conv = convert_speed(val,self.config["from_unit"],self.config["to_unit"])
                elif self.config["measurement_type"]=="Afstand":
                    conv = convert_distance(val,self.config["from_unit"],self.config["to_unit"])
                else:
                    conv = convert_temperature(val,self.config["from_unit"],self.config["to_unit"])
                self.conv_val = f"{conv:.2f}"
            except:
                self.orig_val = "-"
                self.conv_val = "-"
            self.update()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    if os.path.exists("box.json"):
        with open("box.json") as f:
            box = json.load(f)
    else:
        box = {"left":200,"top":200,"width":200,"height":80}
    overlay = Overlay(box)
    sys.exit(app.exec_())
