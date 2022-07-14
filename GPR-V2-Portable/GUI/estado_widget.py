
# Se importan las clases necesarias para construir la interfaz
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout

# Se importa el timer de PyQt5 para actualizar el tiempo restante
from PyQt5.QtCore import QTimer

# Se importa la funcion para convertir segundos en horas, minutos y segundos
from datetime import timedelta


class EstadoWidget(QWidget):

    def __init__(self, p_parent=None):

        # Inicializacion de la clase padre
        super().__init__(parent=p_parent)

        # Se crea el layout principal
        layout = QHBoxLayout()

        # Se crean los objetos del panel izquierdo
        lb0_layout = QVBoxLayout()
        lb0_layout.addWidget(QLabel("<b>Tiempo restante:</b>"))
        lb0_layout.addWidget(QLabel("<b>Puntos restantes:</b>"))

        # Se crea otro layout de widgets
        lb1_layout = QVBoxLayout()
        lb1_layout.addWidget(QLabel("<b>Promedio por punto:</b>"))
        lb1_layout.addWidget(QLabel("<b>Porcentaje completado:</b>"))

        # Se crean los objetos dinamicos del panel
        self.time_lb = QLabel("00:00:00")
        self.points_lb = QLabel("0/0")
        self.avg_lb = QLabel("0 segundos")
        self.porc_lb = QLabel("0%")

        # Se agregan los objetos al panel derecho
        dlb0_layout = QVBoxLayout()
        dlb0_layout.addWidget(self.time_lb)
        dlb0_layout.addWidget(self.points_lb)

        dlb1_layout = QVBoxLayout()
        dlb1_layout.addWidget(self.avg_lb)
        dlb1_layout.addWidget(self.porc_lb)

        layout.addLayout(lb0_layout)
        layout.addLayout(dlb0_layout)
        layout.addLayout(lb1_layout)
        layout.addLayout(dlb1_layout)

        self.setLayout(layout)

        # Se inicializa el timer para actualizar la interfaz
        self.__timer = QTimer()
        self.__timer.timeout.connect(self.remaining_time_slot)
        self.__timer.start(1000)

        self.remaining_time = 0

        # Variable para almacenar el total de puntos que seran recorridos
        self.total_points = 0

    def fijar_puntos_totales(self, p_puntos):
        self.total_points = p_puntos

    def update_widget(self, p_time_arr, p_current_points):

        # Se revisa que el arreglo de tiempos sea una lista de Python
        assert isinstance(p_time_arr, list), "El arreglo ingresado no es una lista de Python"

        # Se calcula el tiempo promedio por punto hasta ahora
        avg_time = sum(p_time_arr) / len(p_time_arr)

        # Se calcula el tiempo restante en base al tiempo promedio
        if p_current_points % 5 == 0:
            self.remaining_time = avg_time * (self.total_points - p_current_points)

        self.update_labels(p_current_points, avg_time)

    def update_labels(self, p_current_points, p_avg_time):

        # Se convierte el tiempo restante en un formato de h:mm:ss
        str0 = str(timedelta(seconds=self.remaining_time)).split('.')[0]

        # Se actualiza la interfaz con los tiempos
        self.time_lb.setText(str0)

        # Se crea el string para el estado de los puntos
        str1 = "%i/%i" % (p_current_points, self.total_points)

        # Se actualizan los puntos en la interfaz
        self.points_lb.setText(str1)

        # Se actualiza el label de tiempo promedio
        str2 = "{:.2f} segundos".format(p_avg_time)
        self.avg_lb.setText(str2)

        # Se actualiza el label del porcentaje completado
        porcentaje = (p_current_points) / self.total_points * 100
        str3 = "{:.2f}%".format(porcentaje)
        self.porc_lb.setText(str3)

    def remaining_time_slot(self):
        """
        Slot que actualiza el tiempo restante del panel cada segundo.
        """
        if self.remaining_time > 0:
            self.remaining_time -= 1
            # Se convierte el tiempo restante en un formato de h:mm:ss
            str0 = str(timedelta(seconds=self.remaining_time)).split('.')[0]

            # Se actualiza la interfaz con los tiempos
            self.time_lb.setText(str0)
        else:
            self.remaining_time = 0
            # Se convierte el tiempo restante en un formato de h:mm:ss
            str0 = str(timedelta(seconds=self.remaining_time)).split('.')[0]

            # Se actualiza la interfaz con los tiempos
            self.time_lb.setText(str0)
