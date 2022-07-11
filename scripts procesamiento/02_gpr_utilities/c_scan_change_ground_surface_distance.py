import argparse
import os
import h5py
import time
import shutil
import numpy as np


def copy_original_file(c_scan_file):
    # Reads the folder of the file, this folder will be used to store the migrated image
    folder = os.path.dirname(c_scan_file)
    # Formats the output file name and copies the original file to the new one
    output_file_name = folder + '/C_Scan_time_ground_distance_changed.h5'
    shutil.copy(c_scan_file, output_file_name)
    time.sleep(1)
    return output_file_name


def change_distance_and_save(c_scan_file, distance, pol):
    # Calls the function to copy the original file into a new one from which the background will be removed
    output_file_name = copy_original_file(c_scan_file)
    # Opens the new file in read and write mode
    output_file = h5py.File(output_file_name, 'r+')
    if pol.lower() == 'x':
        new_distance = output_file['Position/h x-pol'][:]
        new_distance[:] = distance
        del output_file['Position/h x-pol']
        output_file.create_dataset('Position/h x-pol', dtype='f4', data=new_distance, compression="gzip")
    else:
        new_distance = output_file['Position/h y-pol'][:]
        new_distance[:] = distance
        del output_file['Position/h y-pol']
        output_file.create_dataset('Position/h y-pol', dtype='f4', data=new_distance, compression="gzip")
    # Closes the .h5 file
    output_file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Change names')
    parser.add_argument('filename', type=str)
    parser.add_argument('distance', type=float)

    args = parser.parse_args()

    filename = args.filename
    distance = args.distance

    change_distance_and_save(filename, distance, 'x')
