
# Se importa la librería que permite usar funcionalidades del sistema operativo
import sys

# Se importa la clase que permite crear una aplicación
from PyQt5.QtWidgets import QApplication

# Se importa la clase que crea la ventana principal del programa
from GUI.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
