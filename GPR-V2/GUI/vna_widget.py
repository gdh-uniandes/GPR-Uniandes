
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal


class VNAWidget(QWidget):

    # Señal que se emite para conectar el VNA
    connectSignal = pyqtSignal(str)

    # Señal para configurar el sweep del VNA
    sweepSignal = pyqtSignal(float, float, int)

    # Señal para verificar la calibración del VNA
    calibracionSignal = pyqtSignal()

    # Señal para confirmar la ruta de las mediciones
    pathSignal = pyqtSignal(str)

    # Señal para la configuracion por defect
    defaultSignal = pyqtSignal()

    def __init__(self, p_parent=None):

        # Inicializacion de la super clase
        super().__init__(parent=p_parent)

        # Linea para ingresar la direccion IP
        self.input_ip = QLineEdit("192.168.0.10")
        self.input_ip.setInputMask("999.999.999.999")
        self.input_ip.setEnabled(True)

        # Boton para conectarse con el VNA
        self.bt_connect = QPushButton("Conectar")
        self.bt_connect.setEnabled(True)
        self.bt_connect.clicked.connect(self.connect_slot)

        # Boton para configuracion por defecto de ventanas y trazas
        self.bt_default_config = QPushButton("Configuracion por defecto")
        self.bt_default_config.setEnabled(False)
        self.bt_default_config.clicked.connect(self.default_slot)

        # Boton para preset del VNA
        self.bt_preset = QPushButton("Preset")
        self.bt_preset.setEnabled(False)
        #self.bt_preset.clicked.connect(lambda: self.parent().preset())

        # Layout para la configuracion de la direccion IP
        ip_input_layout = QHBoxLayout()
        ip_input_layout.addWidget(QLabel("IP: "))
        ip_input_layout.addWidget(self.input_ip)
        ip_input_layout.addWidget(self.bt_connect)
        ip_input_layout.addWidget(self.bt_default_config)
        ip_input_layout.addWidget(self.bt_preset)

        # Linea para ingresar la frecuencia inicial del barrido
        self.input_start_freq = QLineEdit("600e6")
        self.input_start_freq.setEnabled(False)

        # Linea para ingresar la frecuencia final del barrido
        self.input_stop_freq = QLineEdit("6e9")
        self.input_stop_freq.setEnabled(False)

        # Linea para ingresar la cantidad de puntos del barrido
        self.input_sweep_points = QLineEdit("512")
        self.input_sweep_points.setInputMask("9999")
        self.input_sweep_points.setEnabled(False)

        # Boton para confirmar la configuracion del barrido
        self.bt_sweep = QPushButton("Configurar Sweep")
        self.bt_sweep.setEnabled(False)
        self.bt_sweep.clicked.connect(self.configurar_sweep_slot)

        # Layout para la configuracion del barrido
        sweep_layout = QHBoxLayout()
        sweep_layout.addWidget(QLabel("Start:"))
        sweep_layout.addWidget(self.input_start_freq)
        sweep_layout.addWidget(QLabel("Stop:"))
        sweep_layout.addWidget(self.input_stop_freq)
        sweep_layout.addWidget(QLabel("Points:"))
        sweep_layout.addWidget(self.input_sweep_points)
        sweep_layout.addWidget(self.bt_sweep)

        # Linea para mostrar el estado actual de la calibracion
        self.line_cal_status = QLineEdit("Presione en \"Verificar estado\" para conocer el estado de calibracion")
        self.line_cal_status.setEnabled(False)

        # Boton para preguntar al VNA por el estado de calibracion
        self.bt_ask_cal_status = QPushButton("Verificar estado")
        self.bt_ask_cal_status.setEnabled(False)
        self.bt_ask_cal_status.clicked.connect(self.calibration_slot)

        # Boton para entrar en el menu de calibracion
        self.bt_calibrate = QPushButton("Calibrar VNA")
        self.bt_calibrate.setEnabled(False)
        #self.bt_calibrate.clicked.connect(lambda: self.parent().calibrate_slot())

        # Layout para la calibracion
        calibrate_layout = QHBoxLayout()
        calibrate_layout.addWidget(QLabel("Estado de calibracion:"))
        calibrate_layout.addWidget(self.line_cal_status)
        calibrate_layout.addWidget(self.bt_ask_cal_status)
        calibrate_layout.addWidget(self.bt_calibrate)

        # Linea para preguntar la ruta donde almacenar las mediciones
        self.input_store_route = QLineEdit("C:\\")
        self.input_store_route.setEnabled(False)

        # Boton para confirmar la ruta donde almacenar las mediciones
        self.bt_confirm_route = QPushButton("Confirmar ruta")
        self.bt_confirm_route.setEnabled(False)
        self.bt_confirm_route.clicked.connect(self.path_slot)

        # Layout para la ruta de almacenamiento
        storage_layout = QHBoxLayout()
        storage_layout.addWidget(QLabel("Ruta para almacenar mediciones:"))
        storage_layout.addWidget(self.input_store_route)
        storage_layout.addWidget(self.bt_confirm_route)

        # Layout principal del widget
        widget_layout = QVBoxLayout()
        widget_layout.addLayout(ip_input_layout)
        widget_layout.addLayout(sweep_layout)
        widget_layout.addLayout(calibrate_layout)
        widget_layout.addLayout(storage_layout)
        self.setLayout(widget_layout)

    def connect_slot(self):
        ip = self.input_ip.text()
        self.connectSignal.emit(ip)

    def configurar_sweep_slot(self):
        f_min = float(self.input_start_freq.text())
        f_max = float(self.input_stop_freq.text())
        n_puntos = int(self.input_sweep_points.text())
        self.sweepSignal.emit(f_min, f_max, n_puntos)

    def calibration_slot(self):
        self.calibracionSignal.emit()

    def path_slot(self):
        path = self.input_store_route.text()
        self.pathSignal.emit(path)

    def default_slot(self):
        self.defaultSignal.emit()

    def enable_elements(self):
        self.bt_connect.setEnabled(False)
        self.bt_default_config.setEnabled(True)
        self.bt_preset.setEnabled(True)
        self.bt_ask_cal_status.setEnabled(True)
        self.bt_calibrate.setEnabled(True)
        self.bt_confirm_route.setEnabled(True)
        self.bt_sweep.setEnabled(True)
        self.input_start_freq.setEnabled(True)
        self.input_stop_freq.setEnabled(True)
        self.input_sweep_points.setEnabled(True)
        self.input_store_route.setEnabled(True)

    def disable_elements(self):
        self.bt_connect.setEnabled(True)
        self.bt_default_config.setEnabled(False)
        self.bt_preset.setEnabled(False)
        self.bt_ask_cal_status.setEnabled(False)
        self.bt_calibrate.setEnabled(False)
        self.bt_confirm_route.setEnabled(False)
        self.bt_sweep.setEnabled(False)
        self.input_start_freq.setEnabled(False)
        self.input_stop_freq.setEnabled(False)
        self.input_sweep_points.setEnabled(False)
        self.input_store_route.setEnabled(False)
