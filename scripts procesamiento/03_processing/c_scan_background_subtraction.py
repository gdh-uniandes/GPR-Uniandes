import os
import h5py
import time
import shutil
import numpy as np

import tkinter as tk
from tkinter import filedialog
def copy_original_file(c_scan_file):
    # Reads the folder of the file, this folder will be used to store the migrated image
    folder = os.path.dirname(c_scan_file)
    # Formats the output file name and copies the original file to the new one
    output_file_name = folder + '/C_Scan_time_background_subtracted.h5'
    shutil.copy(c_scan_file, output_file_name)
    time.sleep(1)
    return output_file_name


def remove_background_and_save(c_scan_file, background, pol):
    # Calls the function to copy the original file into a new one from which the background will be removed
    output_file_name = copy_original_file(c_scan_file)
    # Opens the new file in read and write mode
    output_file = h5py.File(output_file_name, 'r+')
    background_file = h5py.File(background, 'r+')
    if pol.lower() == 'x':
        bckg_removed_real = output_file['A-Scan/Re{A-Scan x-pol}'][:] - background_file['A-Scan/Re{A-Scan x-pol}'][:]
        bckg_removed_imag = output_file['A-Scan/Im{A-Scan x-pol}'][:] - background_file['A-Scan/Im{A-Scan x-pol}'][:]
        del output_file['A-Scan/Re{A-Scan x-pol}']
        del output_file['A-Scan/Im{A-Scan x-pol}']
        output_file.create_dataset('A-Scan/Re{A-Scan x-pol}', dtype='f4', data=bckg_removed_real, compression="gzip")
        output_file.create_dataset('A-Scan/Im{A-Scan x-pol}', dtype='f4', data=bckg_removed_imag, compression="gzip")
    else:
        bckg_removed_real = output_file['A-Scan/Re{A-Scan y-pol}'] - background_file['A-Scan/Re{A-Scan y-pol}'][:]
        bckg_removed_imag = output_file['A-Scan/Im{A-Scan y-pol}'] - background_file['A-Scan/Im{A-Scan y-pol}'][:]
        del output_file['A-Scan/Re{A-Scan y-pol}']
        del output_file['A-Scan/Im{A-Scan y-pol}']
        output_file.create_dataset('A-Scan/Re{A-Scan y-pol}', dtype='f4', data=bckg_removed_real, compression="gzip")
        output_file.create_dataset('A-Scan/Im{A-Scan y-pol}', dtype='f4', data=bckg_removed_imag, compression="gzip")
    # Closes the .h5 file
    output_file.close()
    background_file.close()


if __name__ == '__main__':
    # file = 'D:/Daniel/Documents/Examples/05_Lab_GPR/Time/C_Scans/C_Scan_default_title.h5'
    #file = 'D:/Daniel/Documents/02_mediciones_lab/11_arena_alta_mina_350_350/20214101356/C_Scans/C_Scan_time_raw.h5'
    #back = 'D:/Daniel/Documents/02_mediciones_lab/10_caja_arena_alta/2021471440/C_Scans/C_Scan_time_raw.h5'
    root = tk.Tk()
    root.withdraw()
    file = filedialog.askopenfilename(parent=root, initialdir=os.getcwd())
    back = filedialog.askopenfilename(parent=root, initialdir=os.getcwd())
    root.destroy()
    remove_background_and_save(file, back, 'x')
