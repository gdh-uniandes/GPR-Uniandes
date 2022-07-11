import os
import h5py
import time
import shutil
import numpy as np


def copy_original_file(c_scan_file):
    # Reads the folder of the file, this folder will be used to store the migrated image
    folder = os.path.dirname(c_scan_file)
    # Extract the name of archive
    name = os.path.splitext(os.path.basename(c_scan_file))[0]
    # Formats the output file name and copies the original file to the new one
    output_file_name = folder + '/'+ name+'_background_removed.h5'
    shutil.copy(c_scan_file, output_file_name)
    time.sleep(1)
    return output_file_name

# Se modificó el nombre de la función para que no tuviera el mismo que en c_scan_background_subtraction y no diera problemas al importar en main.py
def remove_average_and_save(c_scan_file, pol):
    # Calls the function to copy th eoriginal file into a new one from which the background will be removed
    output_file_name = copy_original_file(c_scan_file)
    # Opens the new file in read and write mode
    output_file = h5py.File(output_file_name, 'r+')
    if pol.lower() == "x":
        avg = np.mean(output_file['A-Scan/Re{A-Scan x-pol}'], 0)
        bckg_removed = output_file['A-Scan/Re{A-Scan x-pol}'] - avg
        del output_file['A-Scan/Re{A-Scan x-pol}']
        output_file.create_dataset('A-Scan/Re{A-Scan x-pol}', dtype='f4', data=bckg_removed, compression="gzip")
    else:
        avg = np.mean(output_file['A-Scan/Re{A-Scan y-pol}'], 0)
        bckg_removed = output_file['A-Scan/Re{A-Scan y-pol}'] - avg
        del output_file['A-Scan/Re{A-Scan y-pol}']
        output_file.create_dataset('A-Scan/Re{A-Scan y-pol}', dtype='f4', data=bckg_removed, compression="gzip")
    # Closes the .h5 file
    output_file.close()


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    file = filedialog.askopenfilename(parent=root, initialdir=os.getcwd())
    root.destroy()
    remove_average_and_save(file, 'x')