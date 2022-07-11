import os
import pandas as pd
import numpy as np

if __name__ == '__main__':
    x = np.linspace(0, 1000, 11)
    y = np.linspace(0, 1000, 5)

    freq_dom = False

    if freq_dom:
        data_header_1 = 'S21_real'
        data_header_2 = 'S21_imag'
    else:
        data_header_1 = 'A-Scan_real'
        data_header_2 = 'A-Scan_imag'

    q = 501

    for i in range(0,len(x)):
        for j in range(0,len(y)):
            data = np.random.rand(q,2)
            h = round(100 + 10*np.random.rand())

            if freq_dom:
                title_x = 'VNA_X' + str(round(x[i])) + '_Y' + str(round(y[j])) + '_OrX_Fs600M_Fe6000M_Qf' + str(q) + \
                          '_H' + str(h) + '.csv'
                title_y = 'VNA_X' + str(round(x[i])) + '_Y' + str(round(y[j])) + '_OrY_Fs600M_Fe6000M_Qf' + str(q) + \
                          '_H' + str(h) + '.csv'
            else:
                title_x = 'Time_X' + str(round(x[i])) + '_Y' + str(round(y[j])) + '_OrX_Ts0u_Te370u_Qt' + str(q) + \
                          '_H' + str(h) + '.csv'
                title_y = 'Time_X' + str(round(x[i])) + '_Y' + str(round(y[j])) + '_OrY_Ts0u_Te370u_Qt' + str(q) + \
                          '_H' + str(h) + '.csv'

            data_frame = pd.DataFrame({data_header_1: data[:, 0], data_header_2: data[:, 1]})

            directory = "D:/OneDrive/OneDrive - Pontificia Universidad Javeriana/2020_10/Andes/Cuarentena/Trazas-B-C/DatasetCSV/TimeDomain/"
            filename = directory + title_x
            data_frame.to_csv(filename, index=False, header=True)
            filename = directory + title_y
            data_frame.to_csv(filename, index=False, header=True)
