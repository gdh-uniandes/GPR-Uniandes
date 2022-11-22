
from GUI.dialogo_trayectorias import TrayectoriasDialogo
from serial.tools.list_ports import comports
from PyQt5.QtWidgets import QWidget, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal


class PosicionadorWidget(QWidget):

    # Señal que se emite cuando se inicia una nueva trayectoria
    trayectoriaSignal = pyqtSignal(list)

    # Señal que se emite cuando se pretende conectar el posicionador
    conectarSignal = pyqtSignal(str)

    # Señal que se emite cuando se pretende desconectar el posicionador
    desconectarSignal = pyqtSignal()

    def __init__(self, p_parent=None):

        # Se inicializa la clase padre
        super().__init__(parent=p_parent)

        # Botón para realizar un recorrido en línea recta
        self.bt_line = QPushButton("Línea recta")
        self.bt_line.setEnabled(False)
        self.bt_line.clicked.connect(self.straight_line_slot)

        # Botón para realizar un recorrido en grilla
        self.bt_grid = QPushButton("Grilla")
        self.bt_grid.setEnabled(False)
        self.bt_grid.clicked.connect(self.grid_slot)

        # Botón para enviar al posicionador a su ubicación inicial
        self.bt_start = QPushButton("Posición inicial")
        self.bt_start.setEnabled(False)
        self.bt_start.clicked.connect(self.initial_position_slot)

        # Boton para conectarse con el posicionador
        self.bt_connect = QPushButton("Conectar")
        self.bt_connect.setEnabled(False)
        self.bt_connect.clicked.connect(self.conectar_slot)

        # Botón para desconectarse del posicionador
        self.bt_disconnect = QPushButton("Desconectar")
        self.bt_disconnect.setEnabled(False)
        self.bt_disconnect.clicked.connect(self.desconectar_slot)

        # Configuración del combobox para seleccionar el puerto serial
        self.com_input = QComboBox()
        self.com_input.setEnabled(True)

        # Se incluyen los puertos seriales conectados
        ports = comports()
        if len(ports) > 0:
            for port in ports:
                self.com_input.addItem(port.device)
            self.bt_connect.setEnabled(True)
        else:
            self.com_input.addItem("No hay puertos seriales disponibles")
            self.bt_connect.setEnabled(False)

        # Boton para actualizar la lista de puertos seriales
        self.bt_update_com = QPushButton("Actualizar")
        self.bt_update_com.setEnabled(True)
        self.bt_update_com.clicked.connect(self.update_com_ports)

        # Layout para la seleccion del puerto serial
        com_input_layout = QHBoxLayout()
        com_input_layout.addWidget(QLabel("Puerto: "))
        com_input_layout.addWidget(self.com_input)
        com_input_layout.addWidget(self.bt_update_com)

        # Layout para conexión y desconexión
        connect_layout = QHBoxLayout()
        connect_layout.addWidget(self.bt_connect)
        connect_layout.addWidget(self.bt_disconnect)

        # Layout de los botones de recorridos
        bt_layout = QHBoxLayout()
        bt_layout.addWidget(self.bt_line)
        bt_layout.addWidget(self.bt_grid)
        bt_layout.addWidget(self.bt_start)

        # Layout principal del widget
        widget_layout = QVBoxLayout()
        widget_layout.addLayout(com_input_layout)
        widget_layout.addLayout(connect_layout)
        widget_layout.addLayout(bt_layout)
        self.setLayout(widget_layout)

    def conectar_slot(self):
        port = self.com_input.currentText()
        self.conectarSignal.emit(port)

    def desconectar_slot(self):
        self.desconectarSignal.emit()

    def straight_line_slot(self):
        try:
            dialogo = TrayectoriasDialogo(p_type=0)
            x_init, x_end, params = dialogo.get_parameters()
            trayectoria = PosicionadorWidget.calcular_trayectoria(p_type=0,
                                                    p_x_init=x_init,
                                                    p_x_end=x_end,
                                                    p_params=params)
            self.trayectoriaSignal.emit(trayectoria)
        except:
            print("No se hara ningun recorrido")

    def grid_slot(self):
        try:
            dialogo = TrayectoriasDialogo(p_type=1)
            x_init, x_end, params = dialogo.get_parameters()
            trayectoria = PosicionadorWidget.calcular_trayectoria(p_type=1,
                                                    p_x_init=x_init,
                                                    p_x_end=x_end,
                                                    p_params=params)
            self.trayectoriaSignal.emit(trayectoria)
        except:
            print("No se hara ningun recorrido")

    def initial_position_slot(self):
        self.trayectoriaSignal.emit([[0, 0]])

    @staticmethod
    def calcular_trayectoria(p_type, p_x_init, p_x_end, p_params):
        if p_type == 0:
            # Se recupera el numero de pasos de los parametros
            n_steps = p_params[0]

            # Se calcula el tamaño de los pasos a partir de los parametros
            dx = (p_x_end[0]-p_x_init[0]) / n_steps
            dy = (p_x_end[1]-p_x_init[1]) / n_steps

            # Se inicializa la lista con los puntos de la trayectoria
            trayectoria = []

            # Se agregan los puntos de la linea recta a la lista
            for i in range(n_steps + 1):
                punto = [p_x_init[0] + i * dx, p_x_init[1] + i * dy]
                trayectoria.append(punto)

        elif p_type == 1:
            # Se recuperan los numeros de pasos de los parametros
            n_steps_x = p_params[0]
            n_steps_y = p_params[1]

            # Se calcula el tamaño de los pasos a partir de los parametros
            dx = (p_x_end[0]-p_x_init[0]) / n_steps_x
            dy = (p_x_end[1]-p_x_init[1]) / n_steps_y

            # Se inicializa la lista con los puntos de la trayectoria
            trayectoria = []

            for_range = list(range(n_steps_y + 1))
            # Se agregan los puntos del recorrido de grilla a la lista
            for i in range(n_steps_x + 1):
                for j in for_range:
                    punto = [p_x_init[0] + i * dx, p_x_init[1] + j * dy]
                    trayectoria.append(punto)
                for_range.reverse()
        # Devuelve la trayectoria que fue calculada
        return trayectoria

    def enable_buttons(self):
        """
        Metodo que activa los botones del panel
        """
        self.bt_line.setEnabled(True)
        self.bt_grid.setEnabled(True)
        self.bt_start.setEnabled(True)
        self.bt_connect.setEnabled(False)
        self.bt_disconnect.setEnabled(True)

    def disable_buttons(self):
        """
        Metodo que desactiva los botones del panel
        """
        self.update_com_ports()
        self.bt_line.setEnabled(False)
        self.bt_grid.setEnabled(False)
        self.bt_start.setEnabled(False)

    def update_com_ports(self):
        self.com_input.clear()
        ports = comports()
        if len(ports) > 0:
            for port in ports:
                self.com_input.addItem(port.device)
            self.bt_connect.setEnabled(True)
            self.bt_disconnect.setEnabled(False)
        else:
            self.com_input.addItem("No hay puertos seriales disponibles")
            self.bt_connect.setEnabled(False)
            self.bt_disconnect.setEnabled(False)
