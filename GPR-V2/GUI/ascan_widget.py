from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np

class AScanWidget(QWidget):

    def __init__(self, p_parent=None):
        super().__init__(parent=p_parent)

        # Inicializa la figura sobre la cual se va a graficar
        self.figure = Figure()

        # Este es el lienzo sobre el cual se va a mostrar la figura
        self.canvas = FigureCanvas(self.figure)

        # Almacena limites para el eje x de la grafica
        self.low_limit = 0
        self.high_limit = 20e-9

        # Se inicializa una grafica desocupada para mantener la estetica
        ax = self.figure.add_subplot(111)
        ax.set_xlabel("Tiempo (s)")
        ax.set_ylabel("Magnitud (V/V)")
        ax.set_xlim(self.low_limit, self.high_limit)
        #ax.set_ylim(-0.04, 0.04)
        ax.grid(b=True)
        ax.set_aspect('auto')
        self.canvas.draw()

        # Boton temporal para obtener la grafica del VNA
        # self.bt_grafica = QPushButton("Generar grafica")
        # self.bt_grafica.setEnabled(True)
        # self.bt_grafica.clicked.connect(lambda : self.parent().plot_a_scan())

        # Layout global para el widget
        widget_layout = QVBoxLayout()
        widget_layout.addWidget(self.canvas)
        # widget_layout.addWidget(self.bt_grafica)

        # Configuracion final del widget
        self.setLayout(widget_layout)
        self.resize(self.sizeHint())

    def plot_a_scan(self, time, ascan, punto):
        ax = self.figure.add_subplot(111)
        ax.clear()
        title = "Traza A para X={} y Y={}".format(int(punto[0]), int(punto[1]))
        ax.set_title(title)
        ax.set_xlabel("Tiempo (s)")
        ax.set_ylabel("Magnitud (V/V)")
        ax.set_xlim(self.low_limit, self.high_limit)
        ax.set_ylim(-0.04, 0.04)
        ax.grid(b=True)
        ax.set_aspect('auto')
        ax.plot(time, ascan)
        self.canvas.draw()
