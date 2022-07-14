
import numpy as np
from os import mkdir

from Funciones.gpr20_ifft import inverse_fast_fourier


class Procesamiento:

    def __init__(self):
        pass

    def formatear_parametros_s(self, s_params):
        s_re = []
        s_im = []

        s_params = s_params[1:]
        head_len = int(s_params[0])
        s_params = s_params[head_len+1:]
        s_params = s_params.split(',')

        for indx  in range(len(s_params)-1):
            if indx % 2 == 1:
                s_im.append(s_params[indx])
            else:
                s_re.append(s_params[indx])

        s_re = np.asarray(s_re, dtype=np.float32)
        s_im = np.asarray(s_im, dtype=np.float32)

        s_complex = s_re + 1j * s_im

        return s_re, s_im, s_complex

    def formatear_frecuencia(self, freq_list):
        freq_list = freq_list[1:]
        head_len = int(freq_list[0])
        freq_list = freq_list[head_len+1:]
        freq_list = freq_list.split(',')
        freq_list.pop()
        freq_list = np.asarray(freq_list, dtype=np.float32)
        df = freq_list[1] - freq_list[0]

        freq_pos = np.arange(0, freq_list[-1], df)
        freq_neg = -1 * np.flip(freq_pos)[0:len(freq_pos)-1]

        full_freq = np.append(freq_neg, freq_pos)
        nf = len(full_freq)
        len_zeros = len(freq_pos) - len(freq_list)

        return freq_list, len_zeros, nf

    def tiempo(self, freq_list):
        df = float(freq_list[1]) - float(freq_list[0])
        Nf = len(freq_list)
        Fs = 2 * Nf * df
        dt = 1 / Fs
        return np.arange(0, Nf * dt / 2, dt)

    def calcular_traza_a(self, s_params, freq_list):
        traza_a, tiempo, _, _ = inverse_fast_fourier(s_params, freq_list)
        return traza_a, tiempo

    def grafica_traza_a(self, traza_a):
        return np.sign(np.imag(traza_a)) * np.abs(traza_a)

    def almacenar_parametros_s(self, s_re, s_im, freq, punto, path):
        fs = freq[0] / 1e6
        fe = freq[-1] / 1e6
        filename = "VNA_X" + str(punto[0]) + "_Y" + str(punto[1]) + "_OrX_Fs" + str(fs) + "M_Fe" + str(fe) + "M_Qf" + str(len(freq)) + "_H810.csv"
        filepath = path + filename
        with open(filepath, 'w+') as csv_file:
            csv_file.write("S21_real,S21_imag\n")
            # assert len(s_re) == len(s_im), "Los datos no tienen igual longitud"
            for indx in range(len(s_re)):
                str_s = str(s_re[indx]) + ',' + str(s_im[indx]) + '\n'
                csv_file.write(str_s)
        # csv_file.close()

    def almacenar_traza_a(self, traza_a, tiempo, punto, path):
        ts = tiempo[0] * 1e6
        te = tiempo[-1] * 1e6
        filename = "Time_X" + str(punto[0]) + "_Y" + str(punto[1]) + "_OrX_Ts" + str(ts) + "u_Te" + str(te) + "u_Qt" + str(len(tiempo)) + "_H150.csv"
        filepath = path + filename
        csv_file = open(filepath, 'w+')
        csv_file.write("A-scan_real,A-scan_imag\n")
        for indx in range(len(tiempo)):
            str_a = str( np.real(traza_a[indx])) + ',' + str(np.imag(traza_a[indx])) + '\n'
            csv_file.write(str_a)
        csv_file.close()

    @staticmethod
    def crear_carpeta(path):
        mkdir(path)
