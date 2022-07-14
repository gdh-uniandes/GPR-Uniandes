import vxi11
import time

class VNA:

    def __init__(self):
        """
            Clase con las funciones basicas del VNA. Permite conectarse, desconectarse y adquirir las mediciones.
            Para referencia sobre los mensajes enviados al VNA por favor consultar el manual "Programing Manual VNA
            Master MS2026C Vector Network Analyzer". En cada funcion de escritura se hace referencia a la pagina del
            manual donde se puede encontrar el comando.
        """
        self.instrument = None
        self.make = None
        self.model = None

    def connect(self, ip):
        """
        Crea la conexion IP entre el VNA y el computador. Pregunta el ID del VNA y retorna la marca y modelo

        Args:
            ip (str): Direccion IP del VNA a conectar.
        """

        # Define la direccion IP del instrumento:
        self.instrument = vxi11.Instrument(ip)

        # Define el timeout del VNA en 30 segundos:
        self.instrument.timeout = 30

        # Abre la conexion con el instrumento:
        self.instrument.open()

        # Pregunta al instrumento por su identificacion (pag. 1-8):
        identification = self.instrument.ask("*IDN?").replace('"', '').split(',')
        self.make = identification[0].upper()
        self.model = identification[1].upper()


    def disconnect(self):
        """
            Desconecta el computador del VNA.
            :arg: self: Objeto de clase VNA
        """
        try:
            self.instrument.close()
            print("VNA desconectado")
        except:
            print("No se pudo desconectar")

    def check_calibration(self):
        """
            Verifica el estado de la calibracion actual del VNA
            :arg: self: Objeto de clase VNA
            :return: message: Estado de la calibracion (string)
        """
        # Pregunta al instrumento por el estado de la calibracion (pag. 3-134):
        calstatus = int(self.instrument.ask(":SENS:CORR:COLL:STAT:ACC?"))
        if calstatus == 1:
            message = "OK: Accuracy High"
        elif calstatus == 2:
            message = "Change in power level: Accuracy moderate"
        elif calstatus == 3:
            message = "Change in temperature: Accuracy moderate"
        elif calstatus == 4:
            message = "X: Accuracy low"
        elif calstatus == 0:
            message = "No calibration data"
        return message

    def preset(self):
        """
            Realiza un preset del VNA
            :arg: self: Objeto de clase VNA
        """
        # Indica al instrumento que debe hacer preset (pag. 2-2):
        self.instrument.write(":SYST:PRES")
        time.sleep(5)

    def set_sweep(self, fstar, fstop, qpoints):
        """
            Define el barrido en frecuencia del VNA
            :arg: self: Objeto de clase VNA
            :arg: fstar: Frecuencia de inicio del barrido (string/int)
            :arg: fstop: Frecuencia de parada del barrido (string/int)
            :arg: qpoints: Cantidad de puntos del barrido (string/int)
        """
        # Indica al intrumento la frecuencia de inicio del barrido (pag: 3-139):
        self.instrument.write(":SENS:FREQ:STAR " + str(fstar))

        # Indica al intrumento la frecuencia de parada del barrido (pag: 3-140):
        self.instrument.write(":SENS:FREQ:STOP " + str(fstop))

        # Indica al intrumento la cantidad de puntos del barrido (pag: 3-144):
        self.instrument.write(":SENS:SWE:POIN " + str(qpoints))

        return self.instrument.ask(":SENS:SWE:POIN?")

    def calibration_setup(self):
        """
            Configuracion de la calibracion del VNA
            :arg: self: Objeto de clase VNA
        """
        # Define el tipo de linea de transmision a calibrar [Coaxial] (pag. 3-133):
        self.instrument.write(":SENS:CORR:COLL:MED COAX")
        # Define el metodo de calibracion [Short-Open-Thru-Load] (pag. 3-133):
        self.instrument.write(":SENS:CORR:COLL:METH SOLT")
        # Define el kit de calibracion para los puertos [Kit N-macho TOSLN50A-18] (pag. 3-124):
        self.instrument.write(":SENS:CORR:COLL:CONN1 NMAL, \"TOSLN50A-18\"")
        self.instrument.write(":SENS:CORR:COLL:CONN2 NMAL, \"TOSLN50A-18\"")
        # Define el tipo de calibracion [Full 2 port] (pag. 3-130):
        self.instrument.write(":SENS:CORR:COLL:TYPE RF2P")

    def calibration(self, standard, port=1):
        """
            Eniva la instruccion de calibracion al VNA para los diferentes estandares y puertos
            :arg: self: Objeto de clase VNA
            :arg: standard: Estandar de calibracion ["OPEN"/"SHORT"/"LOAD"/"THRU"] (string)
            :arg: port: Numero del pueerto a calibrar [1/2] (int)
        """
        if standard != "THRU":
            # Indica al instrumento que estandar de calibracion medir para que puerto (pag. 3-119):
            self.instrument.write(":SENS:CORR:COLL:ACQU "+ standard + "," + str(port))
        else:
            # Indica al instrumento que medira el estandar de calibracion thru (pag. 3-119):
            self.instrument.write(":SENS:CORR:COLL:ACQU THRU,3")
        time.sleep(5)

    def calculate_calibration(self):
        """
            Este comando debe ser ejecutado despues de haber realizado la calibracion para todos los estandares. Cuando
            se ejecuta se ordena al VNA en calcular la calibracion para los puertos.
            :arg: self: Objeto de clase VNA
        """
        # Indica al instrumento que calcule la calibracion de los puertos (pag. 3-133):
        self.instrument.write(":SENS:CORR:COLL:SAVE")
        time.sleep(5)

    def abort_calibration(self):
        """
            Aborta la calibracion que se de los puertos.
            :arg: self: Objeto de clase VNA
        """
        # Indica al instrumento que aborte la calibracion (pag. 3-118):
        self.instrument.write(":SENS:CORR:COLL:ABOR:ALL")

    def set_windows(self,qtraces):
        """
            Configura las ventanas del VNA para el numero de trazas requerido
            :arg: self: Objeto de clase VNA
            :arg: qtraces: Cantidad de trazas (int)
        """
        # Dependiendo de la cantidad de trazas deseadas se configuran las ventanas de la pantalla y las trazas a
        # graficar (pag. 3-81) (pag. 3-145):
        if qtraces == 1:
            self.instrument.write(":DISP:TRACE:FORM SING")
            self.instrument.write(":SENS:TRACE:TOT 1")
        elif qtraces == 2:
            self.instrument.write(":DISP:TRACE:FORM DUAL")
            self.instrument.write(":SENS:TRACE:TOT 2")
        elif qtraces == 3:
            self.instrument.write(":DISP:TRACE:FORM TRI")
            self.instrument.write(":SENS:TRACE:TOT 3")
        elif qtraces == 4:
            self.instrument.write(":DISP:TRACE:FORM QUAD")
            self.instrument.write(":SENS:TRACE:TOT 4")
        # print(self.instrument.ask(":DISP:TRACE:FORM?"))

    def set_trace(self, tnumber, sparameter, format):
        """
            Configura la traza requerida para el parametro S y el formato dado.
            Argumentos:
            self: Objeto de clase VNA
            tnumber: Numero de la traza requerida (int)
            sparameter: Parametro S a configurar en la traza (string)
            format: Formato de la traza (string)
        """
        self.instrument.write(":SENS:TRACE" + str(tnumber) + ":SPAR " + sparameter)
        self.instrument.write(":CALC" + str(tnumber) + ":FORM " + format)

    def ask_current_trace(self, tnumber):
        """
            Pregunta al VNA por la traza requerida en formato real-imaginario.
            Argumentos:
            self: Objeto de clase VNA
            tnumber: Numero de la traza requerida (int)
        """
        trace = self.instrument.ask(":CALC"+ str(tnumber) +":DATA? SDAT")
        return trace

    def ask_freq_vector(self, tnumber):
        """
            Pregunta al VNA por el vector de frequencias.
            Argumentos:
            self: Objeto de clase VNA
        """
        freq = self.instrument.ask(":SENSE" + str(tnumber) + ":FREQ:DATA?")
        return freq
