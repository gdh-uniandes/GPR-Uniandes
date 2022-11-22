
import time
from PyQt5.QtCore import QThread, pyqtSignal

WORKING_TIME = 3600*10
SLEEP_TIME = 10
class MoverPosicionador(QThread):

    # Señal que indica que el posicionador llego a su ubicacion deseada
    arrivedSignal = pyqtSignal(int, list)

    # Señal que indica que el recorrido ha terminado
    finishedSignal = pyqtSignal()

    def __init__(self, p_trayectoria, p_objeto_serial, p_parent=None):

        # Se inicializa la superclase del hilo
        super().__init__(parent=p_parent)

        # Almacena la trayectoria que sera recorrida
        self.trayectoria = p_trayectoria

        # Incorpora el objeto serial a la clase
        self.objeto_serial = p_objeto_serial

        # Almacena la cantidad de puntos en la trayectoria
        self.n_puntos = len(self.trayectoria)

        # Almacena el indice del punto al cual se debe dirigir
        self.index = 0

        # Almacena un indicador que mueve el posicionador al siguiente punto
        self.continuar = True

        # Variable que controla si el hilo sigue corriendo o no
        self.running = True

    def __del__(self):
        self.wait()

    def run(self):
        """

        Returns:

        """
        #last_time = time.time()
        while self.running:

            if self.continuar:
                try:

                    # Recupera el punto de la lista
                    punto = self.trayectoria[self.index]

                    # Indica al posicionador que se mueva a ese punto
                    self.objeto_serial.go_to_point(p_point=(punto[0], punto[1]), p_speed=2000)

                    # Cuando el posicionador llega al punto emite la señal de llegada
                    self.arrivedSignal.emit(self.index, punto)
                    self.continuar = False
                    self.index += 1

                    #actual_time = time.time() - last_time
                    #if actual_time >= WORKING_TIME:
                        #last_time = time.time()
                        #self.objeto_serial.serial_port.write('$SLP'.encode('utf-8'))
                        #while (time.time() - last_time) <= SLEEP_TIME:
                            #print("SLEEP")
                            #pass
                        #self.objeto_serial.serial_port.write(chr('24').encode('utf-8'))
                        #self.objeto_serial.serial_port.write('$X'.encode('utf-8'))
                        #last_time = time.time()

                except AssertionError as ae:
                    print(str(ae))

                except BrokenPipeError as bpe:
                    print(str(bpe))

            if self.index == self.n_puntos:
                self.running = False

    def continuar_recorrido(self):
        self.continuar = True
