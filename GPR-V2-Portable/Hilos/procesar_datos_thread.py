

import time
from PyQt5.Qt import QThread, pyqtSignal


class ProcesarDatos(QThread):

    def __init__(self, traza, punto):
        super().__init__()
        self.traza = traza
        self.punto = punto

    def run(self):
        # print("Ejecutando hilo de procesamiento para X={}, Y={}".format(self.punto[0], self.punto[1]))
        time.sleep(2.0)
        # print("Ha finalizado el hilo de procesamiento para X={}, Y={}".format(self.punto[0], self.punto[1]))

    def __del__(self):
        self.wait()
