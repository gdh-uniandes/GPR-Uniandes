import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from Funciones import gpr20_ifft

def create_ifft_file(directory):
    files = os.listdir(directory)
    path = directory + 'Time/'
    if not os.path.isdir(path):
        os.mkdir(path)

    for file in files:
        df_freq = pd.read_csv(directory + file)
        df_time = pd.DataFrame()
        
        x_index = file.find("_X")
        y_index = file.find("_Y")
        or_index = file.find("_Or")
        fs_index = file.find("_Fs")
        fe_index = file.find("_Fe")
        qf_index = file.find("_Qf")
        h_index = file.find("_H")
        e_index = file.find(".csv")

        x = file[x_index + 2:y_index]
        y = file[y_index + 2:or_index]
        orient = file[or_index + 3:fs_index]
        fs = float(file[fs_index + 3:fe_index - 1]) * 10**6
        fe = float(file[fe_index + 3:qf_index - 1]) * 10**6
        qf = int(file[qf_index + 3:h_index])
        h = file[h_index + 2:e_index]
        
        real_freq = df_freq[df_freq.columns[0]]
        imag_freq = df_freq[df_freq.columns[1]]
        
        freq = np.linspace(fs, fe, qf)
        signal = real_freq.to_numpy() + 1j * imag_freq.to_numpy()
        
        time_signal, time, _, _ = gpr20_ifft.inverse_fast_fourier(signal, freq)
        
        index_start = np.where(time >= 0)[0][0]
        
        real_time_signal = np.real(time_signal[index_start:])
        imag_time_signal = np.imag(time_signal[index_start:])
        
        new_file_name = path + 'TIME_X' + x + '_Y' + y + '_Or' + orient + '_Ts' + str(0) + 'u_Te' + str(round(time[-1] * 10**6, 4)) + 'u_Qt' + str(len(real_time_signal)) + '_H' + h + '.csv'
        
        df_time['A-Scan_real'] = real_time_signal
        df_time['A-Scan_imag'] = imag_time_signal
        
        df_dom = pd.DataFrame()
        df_dom['Time'] = time[index_start:]
        
        df_time.to_csv(new_file_name, index=False)
        df_dom.to_csv(path + 'time', index=False)

if __name__ == '__main__':
    import tkinter as tk
    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(parent=root, initialdir=os.getcwd())
    root.destroy()
    directory += "/"

    create_ifft_file(directory)

    sys.exit()
