import os
import h5py
import time
import shutil
import argparse
import numpy as np


def copy_original_file(c_scan_file):
    # Reads the folder of the file, this folder will be used to store the migrated image
    folder = os.path.dirname(c_scan_file)
    # Formats the output file name and copies the original file to the new one
    output_file_name = folder + '/C_Scan_time_background_removed.h5'
    shutil.copy(c_scan_file, output_file_name)
    time.sleep(1)
    return output_file_name


def remove_background_and_save(c_scan_file, pol):
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
    parser = argparse.ArgumentParser(description='Remove background from scan.')
    parser.add_argument('filepath', type=str, help='filepath of h5 file')
    parser.add_argument('--polarization', default='x', type=str, choices=['x', 'y'], help="polarization")
    args = parser.parse_args()
    file = args.filepath
    polarization = args.polarization
    remove_background_and_save(file, 'x')
