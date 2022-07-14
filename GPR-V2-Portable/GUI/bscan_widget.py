from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

import numpy as np

class BScanWidget(QWidget):

    def __init__(self, p_parent=None):
        super().__init__(parent=p_parent)

        # Inicializa la figura sobre la cual se va a graficar
        self.figure = plt.figure()

        # Este es el lienzo sobre el cual se va a mostrar la figura
        self.canvas = FigureCanvas(self.figure)

        # Almacena limites para el eje x de la grafica
        plt.imshow(np.zeros((141,256)).T, extent=[0, 141, 20e-9, 0], interpolation='nearest',
                       aspect='auto', cmap='seismic', vmin=-np.amax(0.03), vmax=np.amax(0.03))

        plt.xlabel("Trace number")
        plt.ylabel("Time [s]")

        ax = self.figure.gca()
        ax.grid(which='both', axis='both', linestyle='-.')

        cb = plt.colorbar()
        cb.set_label('[V/V]')

        self.canvas.draw()

        # Layout global para el widget
        widget_layout = QVBoxLayout()
        widget_layout.addWidget(self.canvas)

        # Configuracion final del widget
        self.setLayout(widget_layout)
        self.resize(self.sizeHint())

    def plot_b_scan(self,b_scan):
        ax = self.figure.gca()
        ax.clear()

        plt.imshow(b_scan.T, extent=[0, b_scan.shape[0], 20e-9, 0], interpolation='nearest',
                   aspect='auto', cmap='seismic', vmin=-np.amax(0.03), vmax=np.amax(0.03))

        plt.xlabel("Trace number")
        plt.ylabel("Time [s]")

        ax = self.figure.gca()
        ax.grid(which='both', axis='both', linestyle='-.')

        self.canvas.draw()
