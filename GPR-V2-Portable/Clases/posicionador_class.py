# -*- coding: utf-8 -*-

# Paquete de Python para utilizar puertos seriales
import serial

# Paquete de Python para utilizar funciones relacionadas con el tiempo
import time


class Posicionador:

    def __init__(self):
        """
        Clase con las funciones básicas del posicionador. Permite moverlo a un punto y revisar que esté en estado de
        espera.

        Attributes:
            serial_port (serial.Serial):    Objeto del puerto serial para controlar el posicionador. Es 'None' si en su
                                            se lanzó una excepción en su construcción.
        """

        # Se crea el objeto del puerto serial con sus respectivos parámetros
        try:
            self.serial_port = serial.Serial(baudrate=115200,
                                             bytesize=8,
                                             parity=serial.PARITY_NONE,
                                             stopbits=1,
                                             timeout=5)

        # Manejo de excepciones en la creación del puerto serial
        except serial.SerialException:
            serial.serial_port = None
            print("[ERROR] \t El puerto serial no ha sido encontrado, o no ha podido ser configurado")
        except ValueError:
            serial.serial_port = None
            print("[ERROR] \t Algún parámetro no se encuentra dentro de los límites permitidos")

    def connect(self, p_puerto):
        """
        Funcion que permite conectar al programa con el puerto serial del posicionador

        Args:
            p_puerto (str): Puerto serial al cual se va a conectar

        Raises:
            RuntimeError: si el puerto serial ya está abierto

        Returns:
            0 si se ha abierto el puerto correctamente (el retorno va a ser eliminado)
        """

        # Se ajusta el puerto para la comunicacion serial
        self.serial_port.port = p_puerto

        # Revisa que el puerto no esté abierto, y si lo está, lanza una excepción
        if self.serial_port.is_open:
            raise RuntimeError("El puerto serial ya está abierto")
        else:
            self.serial_port.open()
            return 0

    def check_connection(self):
        """
        Metodo que revisa el estado de la conexion con el posicionador

        Returns:
            True si la conexión está activa, False de lo contrario
        """

        # Se envía un comando para revisar la conexión
        try:
            self.serial_port.write("?".encode('utf-8'))
        except serial.SerialTimeoutException:
            print("[ERROR] \t Se ha alcanzado el tiempo de espera maximo para escribir en el puerto serial")
            return False

        # Espera a la respuesta correcta del posicionador
        for i in range(20):
            # Tiempo muerto para la espera
            time.sleep(0.1)

            # Si la respuesta tiene una longitud en especifico, hay conexión
            if self.serial_port.in_waiting >= 56:
                self.serial_port.reset_input_buffer()
                return True

        # Retorna False debido a que no se verificó la conexión
        return False

    def check_idle(self):
        """
        Método que revisa si el posicionador está en espera.

        Raises:
            BrokenPipeError: si existe algún problema en la comunicación con el posicionador

        Returns:
            True si está en espera, False de lo contrario
        """

        # Envía el comando para conocer el estado del posicionador
        try:
            self.serial_port.write("?".encode('utf-8'))
        except serial.SerialTimeoutException:
            raise BrokenPipeError("Se ha alcanzado el tiempo de espera maximo para escribir en el puerto serial")

        # Lee la respuesta hasta encontrar el fin de linea
        read_data = self.serial_port.read_until("CR/LF").decode('utf-8')

        # Revisa si la palabra "Idle" se encuentra en la respuesta
        if "Idle" in read_data:
            return True
        else:
            return False

    def go_to_point(self, p_point, p_speed):
        """
        Funcion que le indica al posicionador que vaya a una ubicación en específico.

        Args:
            p_point (iterable): coordenadas a las cuales debe ir el posicionador.
            p_speed (int): velocidad de movimiento del posicionador.

        Raises:
            AssertionError: si p_point contiene más de dos elementos.
            BrokenPipeError: si la comunicacion con el puerto serial falla.
        """

        # Revisa que solo se indique un par de coordenadas objetivo
        assert len(p_point) == 2, "El punto objetivo debe contener dos coordenadas únicamente"

        # Selecciona el marco de referencia con coordenadas absolutas
        try:
            self.serial_port.write("G90\n".encode('utf-8'))
        except serial.SerialTimeoutException:
            raise BrokenPipeError("Se ha alcanzado el tiempo de espera maximo para escribir en el puerto serial")

        # Envía el comando para que las antenas vayan a su posición deseada
        try:
            command = "G1 X-%d Y-%d F%d\n" % (p_point[0], p_point[1], p_speed)
            self.serial_port.write(command.encode('utf-8'))
        except serial.SerialTimeoutException:
            raise BrokenPipeError("Se ha alcanzado el tiempo de espera maximo para escribir en el puerto serial")

        # Limpia el buffer de entrada del puerto serial
        time.sleep(0.025)
        self.serial_port.reset_input_buffer()

        # Espera que las antenas lleguen a su posición.
        is_running = True
        while is_running:
            # Limpia el buffer de entrada del puerto serial
            self.serial_port.reset_input_buffer()

            # Envía un comando para conocer el estado del posicionador
            try:
                self.serial_port.write("?".encode('utf-8'))
            except serial.SerialTimeoutException:
                raise BrokenPipeError("Se ha alcanzado el tiempo de espera maximo para escribir en el puerto serial")

            # Lee la respuesta desde el puerto serial
            answer = self.serial_port.readline().decode('utf_8')

            # Revisa que "Run" esté en la respuesta del posicionador
            if "Run" in answer:
                is_running = True
            else:
                is_running = False

    def do_homing(self):
        """
        Realiza la rutina de homing del posicionador.

        Raises:
            BrokenPipeError: si la comunicacion con el puerto serial falla.

        Returns:
            0 cuando termina la rutina de homing.
        """
        try:
            self.serial_port.write("?".encode('utf-8'))
            response = self.serial_port.read_until("CR/LF").decode('utf-8')
        except serial.SerialTimeoutException:
            raise BrokenPipeError("Se ha alcanzado el tiempo de espera maximo para escribir en el puerto serial")

        if "Alarm" in response:
            try:
                self.serial_port.write("$H\n".encode('utf-8'))
            except serial.SerialTimeoutException:
                raise BrokenPipeError("Se ha alcanzado el tiempo de espera maximo para escribir en el puerto serial")

            while self.serial_port.in_waiting == 0:
                pass
            while self.serial_port.in_waiting > 0:
                response = self.serial_port.read_until("CR/LF").decode('utf-8')
            if "ok" in response:
                try:
                    self.serial_port.write("G10 L2 P0 X-50 Y-50\n".encode('utf-8'))
                    self.serial_port.reset_input_buffer()
                except serial.SerialTimeoutException:
                    raise BrokenPipeError("Se ha alcanzado el tiempo de espera maximo para escribir en el puerto serial")

                return 0
            else:
                try:
                    self.serial_port.write("".encode('utf-8'))
                except serial.SerialTimeoutException:
                    raise BrokenPipeError("Se ha alcanzado el tiempo de espera maximo para escribir en el puerto serial")
        else:
            return 0

    def ask_current_position(self):
        """
        Pregunta la posicion actual del posicionador.

        Raises:
            BrokenPipeError: si la comunicacion con el puerto serial falla.

        Returns:
            Cadena de texto que responde el posicionador
        """
        try:
            self.serial_port.reset_input_buffer()
            self.serial_port.write("?".encode('utf-8'))
            return self.serial_port.readline().decode('utf-8')
        except serial.SerialTimeoutException:
            raise BrokenPipeError("Se ha alcanzado el tiempo de espera maximo para escribir en el puerto serial")


    def disconnect(self):
        """
        Cierra el puerto serial activo. Debe ser llamado cada vez que se termina de usar el programa principal.

        Raises:
            RuntimeError: si el puerto serial no se ha cerrado de forma exitosa

        Returns:
            0 cuando el puerto se ha cerrado de forma exitosa. (El retorno será eliminado)
        """

        # Revisa que el puerto serial está abierto antes de intentar cerrarlo
        if self.serial_port.is_open:

            # Cierra el puerto serial
            self.serial_port.close()

            # Revisa que el puerto serial se haya cerrado, de lo contrario, lanza una excepción.
            if self.serial_port.is_open:
                raise RuntimeError("El puerto serial no se cerró exitosamente")

            # Devulve el código de salida 0
            return 0

        else:
            return 0
