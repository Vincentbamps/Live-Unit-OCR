import sys
import json
from PyQt5 import QtWidgets

CONFIG_FILE = "config.json"

measurement_options = {
    "Snelheid": ["m/s", "km/h", "mph", "ft/s", "kn"],
    "Afstand": ["mm", "cm", "m", "km", "inch", "ft", "yd", "mile"],
    "Temperatuur": ["C", "F", "K"]
}

class Configurator(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live OCR Converter - Configuratie")
        self.setGeometry(600, 300, 300, 200)

        self.layout = QtWidgets.QVBoxLayout()

        # Selectie type meting
        self.measure_label = QtWidgets.QLabel("Type meting:")
        self.measure_box = QtWidgets.QComboBox()
        self.measure_box.addItems(measurement_options.keys())
        self.measure_box.currentTextChanged.connect(self.update_units)

        # Selectie van-naar eenheden
        self.from_label = QtWidgets.QLabel("Van eenheid:")
        self.from_box = QtWidgets.QComboBox()
        self.to_label = QtWidgets.QLabel("Naar eenheid:")
        self.to_box = QtWidgets.QComboBox()

        # Opslaan knop
        self.save_button = QtWidgets.QPushButton("Opslaan")
        self.save_button.clicked.connect(self.save_config)

        # Layout opbouwen
        self.layout.addWidget(self.measure_label)
        self.layout.addWidget(self.measure_box)
        self.layout.addWidget(self.from_label)
        self.layout.addWidget(self.from_box)
        self.layout.addWidget(self.to_label)
        self.layout.addWidget(self.to_box)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)
        self.load_config()
        self.update_units()

    def update_units(self):
        measurement = self.measure_box.currentText()
        self.from_box.clear()
        self.to_box.clear()
        self.from_box.addItems(measurement_options[measurement])
        self.to_box.addItems(measurement_options[measurement])

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.measure_box.setCurrentText(config["measurement_type"])
                self.update_units()
                self.from_box.setCurrentText(config["from_unit"])
                self.to_box.setCurrentText(config["to_unit"])
        except FileNotFoundError:
            pass

    def save_config(self):
        config = {
            "measurement_type": self.measure_box.currentText(),
            "from_unit": self.from_box.currentText(),
            "to_unit": self.to_box.currentText()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        QtWidgets.QMessageBox.information(self, "Opgeslagen", "Configuratie is opgeslagen!")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Configurator()
    win.show()
    sys.exit(app.exec_())
