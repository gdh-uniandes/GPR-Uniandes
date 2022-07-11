import argparse
import os
import sys
import re
import pandas as pd


def change_names(directory, height):
    files = os.listdir(directory)

    for file in files:
        data_frame = pd.read_csv(directory + '/' + file)

        m = re.search("VNA_X(.+?)_Y(.+?)_OrX_Fs(.+?)M_Fe(.+?)M_Qf(.+?)_H(.+?).csv", file)
        #x_index = file.find("_X")
        #y_index = file.find("_Y")
        #e_index = file.find(".csv")
        if m:
            x = m.group(1)
            y = m.group(2)
            fs = m.group(3)
            fe = m.group(4)
            qf = m.group(5)
        #x = int(float(file[x_index + 2:y_index]))
        #y = int(float(file[y_index + 2:e_index]))
        
        #new_name = directory + '/' + file[0:x_index + 2] + str(x) + file[y_index:y_index + 2] + str(y) + '_OrX_Ts0u_Te23.1u_Qt501_H250.csv'
        #new_name = directory + '/' + file[0:x_index + 2] + str(x) + file[y_index:y_index + 2] + str(y) + '_OrX_Fs600M_Fe6000M_Qf501_H600.csv'
        new_name = f"{directory}/VNA_X{x}_Y{y}_OrX_Fs{fs}M_Fe{fe}M_Qf{qf}_H{height}.csv"
        # data_frame.columns= ['Time', 'A-Scan_real', 'A-Scan_imag']
        
        #data_frame = data_frame.drop(columns = [data_frame.columns[0]])
        data_frame.to_csv(new_name, index=False)

        os.remove(directory + '/' + file)


if __name__ == '__main__':
    # directory = 'D:/Daniel/Documents/Examples/04_Lab_GPR_OG/Original_A_Scan'
    parser = argparse.ArgumentParser(description='Change names')
    parser.add_argument('directory', type=str)
    parser.add_argument('height', type=int)
    args = parser.parse_args()
    directory = args.directory
    height = args.height
    change_names(directory, height)

    sys.exit()