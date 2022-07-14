from PyQt5.QtWidgets import QDialog, QSpinBox, QGridLayout, QLabel, QPushButton, QTextEdit

class TrayectoriasDialogo(QDialog):

    def __init__(self, p_type=0):
        super().__init__()

        # Se almacena el tipo de dialogo que será creado
        self.type = p_type

        # Se crea el layout principal del cuadro de dialogo
        dialog_layout = QGridLayout()

        # Entrada de datos para la coordenada de inicio
        self.input_p_init_x = QSpinBox()
        self.input_p_init_x.setMinimum(0)
        self.input_p_init_x.setMaximum(750)

        self.input_p_init_y = QSpinBox()
        self.input_p_init_y.setMinimum(0)
        self.input_p_init_y.setMaximum(2450)

        # Entrada de datos para la coordenada final
        self.input_p_end_x = QSpinBox()
        self.input_p_end_x.setMinimum(0)
        self.input_p_end_x.setMaximum(750)

        self.input_p_end_y = QSpinBox()
        self.input_p_end_y.setMinimum(0)
        self.input_p_end_y.setMaximum(2450)

        # Se agregan los widgets necesarios para el dialogo
        dialog_layout.addWidget(QLabel("Coord. de inicio (eje x): "), 0, 0)
        dialog_layout.addWidget(self.input_p_init_x, 0, 1)

        dialog_layout.addWidget(QLabel("Coord. de inicio (eje y): "), 1, 0)
        dialog_layout.addWidget(self.input_p_init_y, 1, 1)

        dialog_layout.addWidget(QLabel("Coord. final (eje x): "), 2, 0)
        dialog_layout.addWidget(self.input_p_end_x, 2, 1)

        dialog_layout.addWidget(QLabel("Coord. final (eje y): "), 3, 0)
        dialog_layout.addWidget(self.input_p_end_y, 3, 1)

        # Se crea la interfaz según el tipo definido
        if p_type == 0:
            # Se crea la entrada del numero de pasos para la línea
            self.input_n_steps = QSpinBox()
            self.input_n_steps.setMinimum(0)
            self.input_n_steps.setMaximum(90000)

            dialog_layout.addWidget(QLabel("Número de pasos"), 4, 0)
            dialog_layout.addWidget(self.input_n_steps, 4, 1)

        elif self.type == 1:
            # Entrada de datos para el numero de pasos de la grilla en el eje X
            self.input_n_stepsx = QSpinBox()
            self.input_n_stepsx.setMinimum(0)
            self.input_n_stepsx.setMaximum(90000)

            dialog_layout.addWidget(QLabel("Número de pasos (eje x)"), 4, 0)
            dialog_layout.addWidget(self.input_n_stepsx, 4, 1)

            # Entrada de datos para numero de pasos de la grilla en el eje Y
            self.input_n_stepsy = QSpinBox()
            self.input_n_stepsy.setMinimum(0)
            self.input_n_stepsy.setMaximum(90000)

            dialog_layout.addWidget(QLabel("Número de pasos (eje y)"), 5, 0)
            dialog_layout.addWidget(self.input_n_stepsy, 5, 1)

        else:
            raise Exception("El tipo de dialogo no es correcto")

        self.bt_accept = QPushButton("Aceptar")
        self.bt_accept.clicked.connect(self.accept)

        self.bt_cancel = QPushButton("Cancelar")
        self.bt_cancel.clicked.connect(self.reject)

        dialog_layout.addWidget(self.bt_accept)
        dialog_layout.addWidget(self.bt_cancel)

        self.setLayout(dialog_layout)

    def get_parameters(self):
        if self.exec_() == QDialog.Accepted:
            if self.type == 0:
                x_init = int(self.input_p_init_x.value())
                y_init = int(self.input_p_init_y.value())
                x_end = int(self.input_p_end_x.value())
                y_end = int(self.input_p_end_y.value())
                n_steps = int(self.input_n_steps.value())
                return (x_init, y_init), (x_end, y_end), [n_steps]

            elif self.type == 1:
                x_init = int(self.input_p_init_x.value())
                y_init = int(self.input_p_init_y.value())
                x_end = int(self.input_p_end_x.value())
                y_end = int(self.input_p_end_y.value())
                n_stepsx = int(self.input_n_stepsx.value())
                n_stepsy = int(self.input_n_stepsy.value())
                return (x_init, y_init), (x_end, y_end), [n_stepsx, n_stepsy]
        else:
            return None
