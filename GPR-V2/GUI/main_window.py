

# Se importan las clases que permiten realizar funciones propias del programa
from Clases.vna_class import VNA
from Clases.posicionador_class import Posicionador
from Clases.procesamiento_class import Procesamiento

from GUI.posicionador_widget import PosicionadorWidget
from GUI.vna_widget import VNAWidget
from GUI.puntos_widget import PuntosWidget
from GUI.estado_widget import EstadoWidget
from GUI.ascan_widget import AScanWidget
from GUI.bscan_widget import BScanWidget

from Hilos.mover_posicionador_thread import MoverPosicionador
#from Hilos.procesar_datos_thread import ProcesarDatos

import multiprocessing as mp
from threading import Thread
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer

import time
import datetime


class MainWindow(QWidget):

    def __init__(self):

        # Se inicializa la superclase
        super().__init__()

        # Se inicializa la lista que contiene los procesos
        self.procesos = []

        # Se inicializa una lista que contiene el tiempo de toma de datos para cada punto
        self.time_arr = []

        # Se crea la variable que almacena la ruta donde se almacenan los datos
        self.path = None

        # Variable que contiene la diferencia de tiempo entre cada dato
        self.time = 0

        # Se declara el objeto serial
        self.objeto_serial = Posicionador()

        # Se declara el objeto del VNA
        self.objeto_vna = VNA()

        # Se declara el hilo principal de ejecucion
        self.mover_posicionador = None

        # Se declaran las variables compartidas en memoria por los procesos
        self.sh_time = None
        self.sh_traza_a = None
        self.sh_punto = mp.Array('d', [0, 0])

        # Se inicializan los widgets de la interfaz
        self.widget_posicionador = PosicionadorWidget(p_parent=self)
        self.widget_puntos = PuntosWidget(p_parent=self)
        self.widget_estado = EstadoWidget(p_parent=self)
        self.widget_consola = None
        self.widget_vna = VNAWidget(p_parent=self)
        self.widget_traza_a = AScanWidget(p_parent=self)
        self.widget_traza_b = BScanWidget(p_parent=self)

        # Se conectan las señales de los paneles con sus slots respectivos
        self.widget_posicionador.trayectoriaSignal.connect(self.hacer_trayectoria)
        self.widget_posicionador.conectarSignal.connect(self.conectar_posicionador)
        self.widget_posicionador.desconectarSignal.connect(self.desconectar_posicionador)

        self.widget_vna.connectSignal.connect(self.conectar_vna)
        self.widget_vna.sweepSignal.connect(self.configurar_sweep)
        self.widget_vna.calibracionSignal.connect(self.verificar_calibracion)
        self.widget_vna.pathSignal.connect(self.fijar_ruta)
        self.widget_vna.defaultSignal.connect(self.default_config)

        # Se inicializan los layouts temporales y se agregan los widgets
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        main_layout = QHBoxLayout()

        left_layout.addWidget(self.widget_posicionador, stretch=1)
        left_layout.addWidget(self.widget_puntos, stretch=4)
        left_layout.addWidget(self.widget_estado, stretch=1)
        # left_layout.addWidget()

        right_layout.addWidget(self.widget_vna)
        right_layout.addWidget(self.widget_traza_a)
        right_layout.addWidget(self.widget_traza_b)

        # Se agregan los layouts temporales al layout principal
        main_layout.addLayout(left_layout, stretch=4)
        main_layout.addLayout(right_layout, stretch=4)
        self.setLayout(main_layout)

        # Se ajusta la ventana principal y se lanza
        self.showMaximized()
        self.setWindowTitle("Desminado Humanitario Uniandes")
        self.show()

    def conectar_posicionador(self, p_port):
        try:
            self.objeto_serial.connect(p_puerto=p_port)
            assert self.objeto_serial.check_connection(), "La conexión con el posicionador ha fallado"
            self.objeto_serial.do_homing()
            self.widget_posicionador.enable_buttons()
        except RuntimeError as e:
            print("Ha habido un error intentando conectarse al posicionador")
            print(str(e))

    def desconectar_posicionador(self):
        try:
            self.objeto_serial.disconnect()
            self.widget_posicionador.disable_buttons()
        except RuntimeError as rte:
            print(str(rte))

    def conectar_vna(self, p_ip):
        self.objeto_vna.connect(ip=p_ip)
        self.widget_vna.enable_elements()

    def desconectar_vna(self):
        self.objeto_vna.disconnect()
        self.widget_vna.disable_elements()

    def configurar_sweep(self, f_min, f_max, n_puntos):
        # Se configura el barrido de frecuencias en el VNA
        puntos = int(self.objeto_vna.set_sweep(fstar=f_min, fstop=f_max, qpoints=n_puntos))

        # Se fija la traza como el parámetro S21
        self.objeto_vna.set_trace(tnumber=1, sparameter="S21", format="SMITH")
        # Se define el tamaño del vector para la traza A
        if (puntos % 2):
        	len_traza_a = puntos / 2
        else:
        	len_traza_a = puntos // 2 + 1

        # Se crean los arreglos compartidos en memoria para los procesos
        self.sh_traza_a = mp.Array('d', [0 for i in range(int(len_traza_a))])
        self.sh_time = mp.Array('d', [0 for i in range(int(len_traza_a))])

    def verificar_calibracion(self):
        status = self.objeto_vna.check_calibration()
        self.widget_vna.line_cal_status.setText(status)

    def default_config(self):
        self.objeto_vna.set_windows(1)
        self.objeto_vna.set_trace(tnumber=1, sparameter="S21", format="SMITH")

    def actualizar_traza_a(self):
        th_plot_traza_a = Thread(	target=self.widget_traza_a.plot_a_scan,
                                    args=(self.sh_time, self.sh_traza_a, self.sh_punto))
        th_plot_traza_a.start()

    def fijar_ruta(self, path):
        self.path = path

    # =====================================================
    #       SLOTS PRINCIPALES DEL PROGRAMA
    # =====================================================

    def hacer_trayectoria(self, p_trayectoria):
        """
        Slot que hace que el GPR realice una tryectoria. La función ejecuta las siguientes acciones:
            1. Crea el hilo de movimiento del posicionador con la trayectoria que fue definida.
            2. Actualiza el panel de puntos con la trayectoria que fue definida.
            3. Incializa el panel de estado para dar un estimado del tiempo restante.
            4. Bloquea la interfaz para evitar que se ingrese una nueva trayectoria.

        Args:
            p_trayectoria (list): contiene los puntos con las coordenadas de la trayectoria.
        """
        # Crea la carpeta para almacenar los datos de la trayectoria y guarda su direccion
        date = datetime.datetime.now()
        nombre_carpeta = "/" + str(date.year) + str(date.month) + \
                         str(date.day) + str(date.hour) + str(date.minute) + "/"

        self.path += nombre_carpeta
        Procesamiento.crear_carpeta(self.path)

        # Actualiza la grafica con la nueva trayectoria
        self.widget_puntos.iniciar_trayectoria(p_trayectoria)

        self.time = time.time()
        self.time_arr = []
        self.widget_estado.fijar_puntos_totales(len(p_trayectoria))

        # Se inicia un hilo que actualiza la grafica de la traza A
        #timer_a = QTimer(self)
        #timer_a.timeout.connect(self.actualizar_traza_a)
        #timer_a.start(500)

        # Incia el movimiento del posicionador
        self.mover_posicionador = MoverPosicionador(p_trayectoria, self.objeto_serial)
        self.mover_posicionador.arrivedSignal.connect(self.arrivedSlot)
        self.mover_posicionador.start()

    def arrivedSlot(self, p_index, p_punto):
        """
        Slot que se ejecuta cuando el posicionador llega a un punto. La funcion ejecuta las siguientes acciones:

        Args:
            p_index (int): indice del punto al cual ha llegado el posicionador.
            p_punto (list): coordenadas del punto al cual ha llegado el posicionador.
        """
        
        # Actualiza la grafica en el nuevo punto
        th_puntos = Thread(target=self.widget_puntos.actualizar_punto, args=(p_index, ))
        th_puntos.start()

        self.sh_punto = p_punto

        # Calula el tiempo entre las llegadas
        actual_time = time.time()
        delta_time = actual_time - self.time
        self.time = actual_time
        self.time_arr.append(delta_time)

        # Actualiza el panel de estado con el punto al que llego y el arreglo de los tiempos
        th_estado = Thread(target=self.widget_estado.update_widget, args=(self.time_arr, p_index+1, ))
        th_estado.start()

        try:
            time.sleep(0.1)
            params = self.objeto_vna.ask_current_trace(tnumber=1)
            freq = self.objeto_vna.ask_freq_vector(tnumber=1)
        except Exception as e:
            print(str(e))

        try:
            # Lanza el hilo que realiza el procesamiento de los datos
            proceso = mp.Process(	target=self.procesar_datos, 
                                    args=(params,
                                          self.sh_punto,
                                          freq,
                                          self.path,
                                          self.sh_traza_a,
                                          self.sh_time))
            proceso.start()
            self.procesos.append(proceso)
            for p in self.procesos:
                p.join()

        except Exception as e:
            print(str(e))

        # Le indica al posicionador que puede continuar con el recorrido
        self.mover_posicionador.continuar_recorrido()

    def procesar_datos(self, param_s, punto, freq, path, sh_traza_a, sh_tiempo):

        # Se crea una instancia de la clase para procesar los datos
        procesamiento = Procesamiento()

        # Se separan los parámetros en parte real e imaginaria y un único número complejo
        s_re_val, s_im_val, s_complex = procesamiento.formatear_parametros_s(param_s)

        # Se realiza el formato del vector de frecuencias
        freq, len_zeros, Nf = procesamiento.formatear_frecuencia(freq)

        # Se crea el vector de tiempo para la traza A
        #tiempo = procesamiento.tiempo(freq)

        # Se crea la traza A con los parametros de dispersion
        #traza_a = procesamiento.calcular_traza_a(s_complex, len(tiempo), len_zeros, Nf)

        # Se crea la traza A que será graficada
        #traza_a_grafica = procesamiento.grafica_traza_a(traza_a)

        #try:
            # Se actualizan las variables compartidas para la traza A
            #for indx in range(len(traza_a)):
                #sh_traza_a[indx] = traza_a_grafica[indx]
                #sh_tiempo[indx] = tiempo[indx]
            # Se almacenan los valores de los parametros de la traza A
            #procesamiento.almacenar_traza_a(traza_a, tiempo, punto, path)
        #except:
            #print("No se graficara o almacenara la TRAZA A")

        # Se actualizan las variables compartidas para la traza B
        # TODO: actualizar variables traza B

        # Se almacenan los valores de los parametros de dispersion
        procesamiento.almacenar_parametros_s(s_re_val, s_im_val, freq, punto, path)


        del procesamiento
