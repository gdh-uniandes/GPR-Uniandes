

from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import AutoMinorLocator, MultipleLocator

class PuntosWidget(QWidget):

    def __init__(self, p_parent=None):

        # Se inicializa la super clase
        super().__init__(parent=p_parent)

        # Se define el atributo que contiene los puntos de la trayectoria
        self.trayectoria = []

        # Inicializa la figura sobre la cual se va a graficar
        self.figure = Figure()

        # Este es el lienzo sobre el cual se va a mostrar la figura
        self.canvas = FigureCanvas(self.figure)

        # Se inicializa una grafica desocupada para mantener la estetica
        ax = self.figure.add_subplot(111)
        ax.set_ylabel("Eje X")
        ax.set_xlabel("Eje Y")
        ax.set_xlim(-50, 1750)
        ax.set_ylim(-50, 750)
        ax.xaxis.set_major_locator(MultipleLocator(100))
        ax.yaxis.set_major_locator(MultipleLocator(100))
        ax.xaxis.set_minor_locator(AutoMinorLocator(5))
        ax.yaxis.set_minor_locator(AutoMinorLocator(5))
        ax.grid(which='major', linestyle='--')
        ax.grid(which='minor', linestyle=':')
        ax.set_aspect('equal')
        self.canvas.draw()

        # Layout global para el widget
        widget_layout = QVBoxLayout()
        widget_layout.addWidget(self.canvas)

        # Configuracion final del widget
        self.setLayout(widget_layout)
        self.resize(self.sizeHint())

    def iniciar_trayectoria(self, p_trayectoria):
        """

        Args:
            p_trayectoria (list): lista con los puntos de la trayectoria que será realizada
        """

        # Reinicia la lista que contiene los puntos de la trayectoria
        self.trayectoria = []
        for punto in p_trayectoria:
            punto.append(False)
            self.trayectoria.append(punto)

        self.clear_plot()
        self.plot_trajectory()

    def actualizar_punto(self, p_index):
        
        # Actualiza los puntos para marcarlos como visitados
        self.trayectoria[p_index][2] = True
        
        if p_index % 3 == 0:
            self.plot_trajectory()
        else:
            pass

    def plot_trajectory(self):

        # Crea un axis para realizar las graficas
        ax = self.figure.add_subplot(111)

        # Borra la anterior figura
        ax.clear()

        # Agrega titulos a los ejes
        ax.set_ylabel("Eje X")
        ax.set_xlabel("Eje Y")

        # Define los límites del foso
        ax.set_xlim(-50, 1750)
        ax.set_ylim(-50, 750)

        ax.xaxis.set_major_locator(MultipleLocator(100))
        ax.yaxis.set_major_locator(MultipleLocator(100))

        ax.xaxis.set_minor_locator(AutoMinorLocator(5))
        ax.yaxis.set_minor_locator(AutoMinorLocator(5))

        ax.grid(which='major', linestyle='--')
        ax.grid(which='minor', linestyle=':')

        ax.set_aspect('equal')

        # Diccionario de los colores
        color_dict = {True: "g", False: "r"}

        X = []
        Y = []
        C = []
        for punto in self.trayectoria:
            X.append(punto[0])
            Y.append(punto[1])
            C.append(color_dict[punto[2]])

        ax.scatter(Y, X, c=C, s=2)

        # Dibuja los puntos del axis. Equivalente en interfaz a plt.show()
        self.canvas.draw()

    def clear_plot(self):
        """
        Metodo que limpia la grafica de los puntos del programa.
        """
        ax = self.figure.add_subplot(111)
        ax.set_xlim(-50, 1750)
        ax.set_ylim(-50, 750)
        ax.xaxis.set_major_locator(MultipleLocator(100))
        ax.yaxis.set_major_locator(MultipleLocator(100))
        ax.xaxis.set_minor_locator(AutoMinorLocator(5))
        ax.yaxis.set_minor_locator(AutoMinorLocator(5))
        ax.grid(which='major', linestyle='--')
        ax.grid(which='minor', linestyle=':')
        ax.set_aspect('equal')
        self.canvas.draw()


