import sys
import os
import glob
import re
import pandas as pd
import h5py

import tkinter as tk
from tkinter import filedialog

def sort_files(file_names):
    """Sorting function for a file list
    Args:
        file_names (list string): List of all file names to be sorted
    Returns:
        sorted_files (list string): Sorted list of file names.
    """
    # Anonymous function - Converts a string into integers or lower case letters
    convert = lambda name: int(name) if name.isdigit() else name.lower()
    # Anonymous function - Splits numbers and alpha-characters from a string then it calls convert for each segment
    alphanumeric_key = lambda key: [convert(character) for character in re.split('([0-9]+)', key)]
    # Files are sorted with a natural order as they are split by the alphanumeric_key function
    sorted_files = sorted(file_names, key = alphanumeric_key)

    return sorted_files

def read_file_names(folder):
    """Function for reading the names of several A-Scan files in a folder/directory
    Args:
        folder (string): Route for the folder/directory with the A-Scan files
    Returns:
        scan_files (list string): List of A-Scan file names
    """

    # Reads the name of the files with .out, .h5 and .csv extension in the folder/directory
    gprmax_files_dot_out = glob.glob(folder + "/*.out")
    gprmax_files_dot_h5 = glob.glob(folder + "/*.h5")
    gpr_files = glob.glob(folder + "/*.csv")

    # Determines which type of files are being read (gprMax or GPR) and stores the list of names
    if not gprmax_files_dot_out:
        if not gprmax_files_dot_h5:
            scan_files = gpr_files
        else:
            scan_files = gprmax_files_dot_h5
    else:
        scan_files = gprmax_files_dot_out

    # If more than one type of file was found in the folder/directory a message prompts that the gprMax .out files will
    # be returned by this function
    if gprmax_files_dot_out and gprmax_files_dot_h5 or gprmax_files_dot_out and gpr_files or \
                    gprmax_files_dot_h5 and gpr_files:
        print("More than one type of A-Scan file was found in the folder/directory")
        print("By default, gprMax .out files will be returned in the sorted list")

    # Raises exception if the selected folder does not contain files with supported extensions
    if not gprmax_files_dot_out and not gprmax_files_dot_h5 and not gpr_files:
        raise Exception("Files in the selected folder/directory do not comply with the supported file extensions")

    # Files are sorted in natural order by sort_files function
    scan_files = sort_files(scan_files)

    return scan_files

def store_c_scan_gprmax_input(folder):
    """Creates a .h5 file to store the the C-Scan in a 3D matrix of dimensions max(col),max(row),len(amplitude)
    Args:
        folder (string): Route for the folder/directory with the gprMax input file
    Returns:
        p (char): Direction of polarization of the source ('X' for x-polarization, 'Y' for y-polarization, 'Z' for
        z-polarization, or 'U' for unknown polarization). Polarization detection is limited to a single source and to
        one of the following sources: hertzian dipole, magnetic dipole, voltage source or transmission line
        h (float): Height of the ground surface. Height will be (-1) if the ground cannot be found. Ground is
        identified by material key-names: 'Ground' or 'Soil' (non-case-sensitive)
        av_h_flag (bool): Flag that tells whether or not the height reported is the actual height or the average.
        Average height is reported when the ground has surface roughness. ('True' Average height for surface roughness,
         'False' Actual height)
    """

    # Return variables are set to their default values
    p = 'U'
    h = -1
    av_h_flag = False

    # Finds the input file for the A-Scans
    input_file = glob.glob(folder + "/*.in")[0]

    if not input_file:
        raise Exception("Input file not detected in folder")

    # Opens the input file in read mode
    file = open(input_file, 'r')

    # Reads the input file line by line
    for line in file:
        line = line.lower()
        # Checks if the current line being read contains information about the source with the key words 'dipole',
        # 'voltage' and 'line'
        if 'dipole' in line:
            # Checks whether the source is coded with a hash command or a Python command and then reads the
            # polarization accordingly
            if '#' in line:
                p_index = line.find(":")
                p = line[p_index + 2].upper()
            else:
                p_index = line.find("(")
                p = line[p_index + 2].upper()
        if 'voltage' in line:
            # Checks whether the source is coded with a hash command or a Python command and then reads the
            # polarization accordingly
            if '#' in line:
                p_index = line.find(":")
                p = line[p_index + 2].upper()
            else:
                p_index = line.find("(")
                p = line[p_index + 2].upper()
        if 'line' in line:
            # Checks whether the source is coded with a hash command or a Python command and then reads the
            # polarization accordingly
            if '#' in line:
                p_index = line.find(":")
                p = line[p_index + 2].upper()
            else:
                p_index = line.find("(")
                p = line[p_index + 2].upper()
        # Checks if the current line being read contains information about the ground/soil
        if 'soil' in line or 'ground' in line:
            # Checks if the 'soil' and 'ground' key-words are in a fractal box command or if they are in a box command
            if 'fractal' in line:
                # If they are in a fractal box command the roughness command is looked for in the input file
                for line_2 in file:
                    if 'roughness' in line_2:
                        # If roughness is found the ground surface is not flat. The the height will be given as the
                        # average of the highest point and the lowest point
                        av_h_flag = True
                        parts = line_2.split()
                        hl = float(parts[10])
                        hh = float(parts[11])
                        h = (hh + hl) / 2
                if h == -1:
                    # If the roughness command is not found, then the fractal box has a flat surface. The height
                    # is retrieved from the fractal box line
                    av_h_flag = False
                    parts = line.split()
                    h = float(parts[6])
            elif 'box' in line:
                # If the ground/soil command is found in a box command then the surface is flat. The height is
                # retrieved from the box line
                av_h_flag = False
                parts = line.split()
                h = float(parts[6])

    return p, h, av_h_flag

def store_c_scan_gprmax_dot_out(scan_files, output_file, p, h, av_h_flag):
    """Populates a .h5 file with the C-Scan and its metadata for A-Scan .out files
    Args:
        scan_files (list string): List of A-Scan file names
        output_file (h5 object): File where the C-Scan is stored
        field_comp (string): Field component to be saved in the merged C-Scan file
    """

    # All of the C-Scan files are stored assuming the A-Scan data come from a square/rectangle lattice of survey points
    # therefore the information needed to recover the position of each measurement is reduced to knowing the first
    # surveyed coordinate (x0, y0), the steps on each direction (dx, dy) and the final coordinate (xf, yf). This
    # information is stored under a group within the output file '/Position'

    # Creates a group in the .h5 file to store the position of the measurement
    pos_grp = output_file.create_group('/Position')

    # The first A-Scan file is opened in read mode to retrieve the position parameters
    data_frame = h5py.File(scan_files[0], 'r')
    # Position from Tx and Rx is retrieved
    rx_pos = data_frame['rxs/rx1'].attrs['Position']
    tx_pos = data_frame['srcs/src1'].attrs['Position']
    # The midpoint between the Tx and Rx is calculated and stored as the first coordinate of the measurement.
    # Position from gprMax files is given in meters and is stored into the merged file in meters too
    pos_grp.attrs['x0'] = (rx_pos[0] + tx_pos[0]) / 2
    pos_grp.attrs['y0'] = (rx_pos[1] + tx_pos[1]) / 2

    data_frame.close()

    # The last A-Scan file is opened in read mode to retrieve the position parameters
    data_frame = h5py.File(scan_files[-1], 'r')
    # Position from Tx and Rx is retrieved
    rx_pos = data_frame['rxs/rx1'].attrs['Position']
    tx_pos = data_frame['srcs/src1'].attrs['Position']
    # The midpoint between the Tx and Rx is calculated and stored as the first coordinate of the measurement.
    # Position from gprMax files is given in meters and is stored into the merged file in meters too
    pos_grp.attrs['xf'] = (rx_pos[0] + tx_pos[0]) / 2
    pos_grp.attrs['yf'] = (rx_pos[1] + tx_pos[1]) / 2

    # Checks whether the height of the ground surface was retrieved
    if h != -1:
        # If the height was retrieved, the height of the antennas in reference to the ground surface is calculated and
        # stored in the output file. Flag that tells if the height given was an average from a rough surface is stored
        # in the output file under 'surface roughness' attribute
        pos_grp.attrs['h'] = tx_pos[2] - h
        pos_grp.attrs['surface roughness'] = av_h_flag
    else:
        # If the height was not retrieved the output file attribute is populated with the word 'Unknown'
        pos_grp.attrs['h'] = 'Unknown'
        pos_grp.attrs['surface roughness'] = av_h_flag

    # Creates a group in the .h5 file to store the time domain parameters of the measurement
    dom_grp = output_file.create_group('/Time')

    # The time values are stored in seconds in the output file
    dom_grp.attrs['t0'] = 0
    dom_grp.attrs['tf'] = data_frame.attrs['Iterations'] * data_frame.attrs['dt']
    dom_grp.attrs['dt'] = data_frame.attrs['dt']
    dom_grp.attrs['q'] = data_frame.attrs['Iterations']

    # Checks if polarization was determined from the input file
    if p == 'U':
        try:
            # If it was not determined it will try to retrieve the information from the output file. If it is found it
            # is stored into variable p
            p = data_frame['srcs/src1'].attrs['Polarisation'].upper()
        except:
            # If it was not found it will prompt that all field components will be saved into the output file
            print("Polarization information could not be found. All field components will be stored in the output file")

    data_frame.close()

    # Creates flags to know when the change in x and y coordinates are changed. This flags are used to determine the dx
    # and dy steps of the lattice.
    dx_flag = False
    dy_flag = False

    # Creates lists used to store the parameters that vary with each A-Scan
    amp_x = []
    amp_y = []
    amp_z = []

    # Loop to read all of the A-Scan files
    for i in range(0, len(scan_files)):
        # A-Scan file is opened and data from it is stored in the data_frame variable
        data_frame = h5py.File(scan_files[i], 'r')

        # Amplitude of the E-field components is retrieved
        if p == 'X':
            amp_x.append(list(data_frame['rxs/rx1/Ex']))
        elif p == 'Y':
            amp_y.append(list(data_frame['rxs/rx1/Ey']))
        elif p == 'Z':
            amp_z.append(list(data_frame['rxs/rx1/Ez']))
        else:
            amp_x.append(list(data_frame['rxs/rx1/Ex']))
            amp_y.append(list(data_frame['rxs/rx1/Ey']))
            amp_z.append(list(data_frame['rxs/rx1/Ez']))

        if not dx_flag and i > 0:
            curr_x = data_frame['srcs/src1'].attrs['Position'][0]

            if curr_x != prev_x:
                pos_grp.attrs['dx'] = curr_x - prev_x
                dx_flag = True

        if not dy_flag and i > 0:
            curr_y = data_frame['srcs/src1'].attrs['Position'][1]

            if curr_y != prev_y:
                pos_grp.attrs['dy'] = curr_y - prev_y
                dy_flag = True

        prev_x = data_frame['srcs/src1'].attrs['Position'][0]
        prev_y = data_frame['srcs/src1'].attrs['Position'][1]

        data_frame.close()

    # A group to store the A-Scan measurements '/A-Scan'
    asc_grp = output_file.create_group('/A-Scan')

    # A-Scan values are stored in data-sets under the '/A-Scan' group. Depending on the source polarization different
    # components are stored
    if p == 'X':
        asc_grp.create_dataset('Re{A-Scan x-pol}', (len(amp_x), len(amp_x[0])), dtype='f4', data=amp_x, compression="gzip")
    elif p == 'Y':
        asc_grp.create_dataset('Re{A-Scan y-pol}', (len(amp_y), len(amp_y[0])), dtype='f4', data=amp_y, compression="gzip")
    elif p == 'Z':
        asc_grp.create_dataset('Re{A-Scan z-pol}', (len(amp_z), len(amp_z[0])), dtype='f4', data=amp_z, compression="gzip")
    else:
        asc_grp.create_dataset('Re{A-Scan x-pol}', (len(amp_x), len(amp_x[0])), dtype='f4', data=amp_x, compression="gzip")
        asc_grp.create_dataset('Re{A-Scan y-pol}', (len(amp_y), len(amp_y[0])), dtype='f4', data=amp_y, compression="gzip")
        asc_grp.create_dataset('Re{A-Scan z-pol}', (len(amp_z), len(amp_z[0])), dtype='f4', data=amp_z, compression="gzip")

def store_c_scan_gpr(scan_files, output_file):
    """Populates a .h5 file with the C-Scan and its metadata for A-Scan .csv files
    Args:
        scan_files (list string): List of A-Scan file names
        output_file (h5 object): File where the C-Scan is stored
    """

    # All of the C-Scan files are stored assuming the A-Scan data come from a square/rectangle lattice of survey points
    # therefore the information needed to recover the position of each measurement is reduced to knowing the first
    # surveyed coordinate (x0, y0), the steps on each direction (dx, dy) and the final coordinate (xf, yf). This
    # information is stored under a group within the output file '/Position'

    # Creates a group in the .h5 file to store the position of the measurement
    pos_grp = output_file.create_group('/Position')

    # Looks for the first coordinate (x0,y0) and the last coordinate (xf,yf) of the A-Scan list
    # As x-y data is stored at the title of the files, identifiers are looked for in the title of the first A-Scan file.
    # The identifier for antenna orientation is also looked for as it indicates the end of the y coordinate.
    x_index = scan_files[0].find("_X")
    y_index = scan_files[0].find("_Y")
    o_index = scan_files[0].find("_Or")
    xf_index = scan_files[-1].find("_X")
    yf_index = scan_files[-1].find("_Y")
    of_index = scan_files[-1].find("_Or")

    # Coordinates are stored in the output file under the '/Position' group. The title of the A-Scan files give the
    # position information in mm, so the value is dived by 1000 to store it in meters
    pos_grp.attrs['x0'] = float(scan_files[0][x_index + 2:y_index]) / 1000
    pos_grp.attrs['y0'] = float(scan_files[0][y_index + 2:o_index]) / 1000
    pos_grp.attrs['xf'] = float(scan_files[-1][xf_index + 2:yf_index]) / 1000
    pos_grp.attrs['yf'] = float(scan_files[-1][yf_index + 2:of_index]) / 1000

    # Title of A-Scan files also contain time/frequency domain information common to all A-Scans. Measurements for both
    # domains can describe the domain completely using the initial value f0 or t0, the step df or dt, the final
    # value ff, and the amount of points. This information is stored under a group within the output file '/Time' or
    # '/Frequency'

    # The domain of the measurement can be known by reading the first word of the file title. Title of frequency domain
    # measurements start with 'VNA' and title of time domain measurements start with 'Time'
    freq_dom = False
    time_dom = False
    if "VNA" in scan_files[0]:
        freq_dom = True
        dom_grp = output_file.create_group('/Frequency')

        # Frequency domain parameters are stored in the title of the files, identifiers are looked for in the title of
        # the first A-Scan file. The identifier for the height of the antennas from the floor is also looked for as it
        # indicates the end of the frequency information
        s_index = scan_files[0].find("_Fs")
        e_index = scan_files[0].find("_Fe")
        q_index = scan_files[0].find("_Qf")
        h_index = scan_files[0].find("_H")

        # The frequency values in the title are written in MHz these values are stored in Hz in the output file
        dom_grp.attrs['f0'] = float(scan_files[0][s_index + 3:e_index - 1]) * 10 ** 6
        dom_grp.attrs['ff'] = float(scan_files[0][e_index + 3:q_index - 1]) * 10 ** 6
        dom_grp.attrs['q'] = float(scan_files[0][q_index + 3:h_index])
        dom_grp.attrs['df'] = (dom_grp.attrs['ff'] - dom_grp.attrs['f0']) / (dom_grp.attrs['q'] - 1)
    else:
        time_dom = True
        dom_grp = output_file.create_group('/Time')

        # Time domain parameters are stored in the title of the files, identifiers are looked for in the title of
        # the first A-Scan file. The identifier for the height of the antennas from the floor is also looked for as it
        # indicates the end of the frequency information
        s_index = scan_files[0].find("_Ts")
        e_index = scan_files[0].find("_Te")
        q_index = scan_files[0].find("_Qt")
        h_index = scan_files[0].find("_H")

        # The time values in the title are written in us these values are stored in s in the output file
        dom_grp.attrs['t0'] = float(scan_files[0][s_index + 3:e_index - 1]) * 10 ** -6
        dom_grp.attrs['tf'] = float(scan_files[0][e_index + 3:q_index - 1]) * 10 ** -6
        dom_grp.attrs['q'] = float(scan_files[0][q_index + 3:h_index])
        dom_grp.attrs['dt'] = (dom_grp.attrs['tf'] - dom_grp.attrs['t0']) / (dom_grp.attrs['q'] - 1)

    # Creates lists used to store the parameters that vary with each A-Scan
    height_x_pol = []
    height_y_pol = []
    real_part_x_pol = []
    imag_part_x_pol = []
    real_part_y_pol = []
    imag_part_y_pol = []

    # Creates flags to know when the change in x and y coordinates are changed. This flags are used to determine the dx
    # and dy steps of the lattice.
    dx_flag = False
    dy_flag = False

    for i in range(0, len(scan_files)):
        # Parameters that change with each survey are stored into the output file inside this loop. The parameters that
        # change are the values of the A-Scan (S21/TD response) and the height of the antennas from the surface

        # The change in x or y coordinates is verified if the dx_flag or dy_flag are False. When these flags are False
        # the system does not have the step information yet. The flags are raised to True when the step is known and
        # the step size is stored in the output file under the '/Position' group
        if not dx_flag and i > 0:
            xc_index = scan_files[i].find("_X")
            yc_index = scan_files[i].find("_Y")
            xp_index = scan_files[i - 1].find("_X")
            yp_index = scan_files[i - 1].find("_Y")

            curr_x = float(scan_files[i][xc_index + 2:yc_index]) / 1000
            prev_x = float(scan_files[i - 1][xp_index + 2:yp_index]) / 1000

            if curr_x != prev_x:
                pos_grp.attrs['dx'] = curr_x - prev_x
                dx_flag = True

        if not dy_flag and i > 0:
            yc_index = scan_files[i].find("_Y")
            oc_index = scan_files[i].find("_Or")
            yp_index = scan_files[i - 1].find("_Y")
            op_index = scan_files[i - 1].find("_Or")

            curr_y = float(scan_files[i][yc_index + 2:oc_index]) / 1000
            prev_y = float(scan_files[i - 1][yp_index + 2:op_index]) / 1000

            if curr_y != prev_y:
                pos_grp.attrs['dy'] = curr_y - prev_y
                dy_flag = True

        # The height of the antennas from the ground surface is a single value parameter for each A-Scan and is stored
        # under the '/Position' group of the output file. The height identifier in the title and the extension indexes
        # are looked for in order to read the height
        h_index = scan_files[i].find("_H")
        c_index = scan_files[i].find(".csv")

        # The polarization of the antennas is determined and then the value is stored in the corresponding array
        o_index = scan_files[i].find("_Or")

        if freq_dom:
            s_index = scan_files[i].find("_Fs")
            # The .csv A-Scan file is opened using pandas csv reader
            data_frame = pd.read_csv(scan_files[i], usecols=["S21_real", "S21_imag"])
        if time_dom:
            s_index = scan_files[i].find("_Ts")
            # The .csv A-Scan file is opened using pandas csv reader
            data_frame = pd.read_csv(scan_files[i], usecols=["A-Scan_real", "A-Scan_imag"])

        orientation = scan_files[i][o_index + 3:s_index]

        # The height and A-Scan values are stored into the arrays corresponding the polarization
        if orientation == 'X':
            # Height value for the A-Scan measurement is stored in a list element  (in meters)
            height_x_pol.append(float(scan_files[i][h_index + 2:c_index]) / 1000)
            real_part_x_pol.append(data_frame.values[:,0])
            imag_part_x_pol.append(data_frame.values[:,1])
        if orientation == 'Y':
            # Height value for the A-Scan measurement is stored in a list element (in meters)
            height_y_pol.append(float(scan_files[i][h_index + 2:c_index]) / 1000)
            real_part_y_pol.append(data_frame.values[:, 0])
            imag_part_y_pol.append(data_frame.values[:, 1])

    # Height values are stored in data-sets under the '/Position' group
    if height_x_pol:
        pos_grp.create_dataset('h x-pol', (len(height_x_pol), 1), dtype='f4', data=height_x_pol, compression="gzip")
    if height_y_pol:
        pos_grp.create_dataset('h y-pol', (len(height_y_pol), 1), dtype='f4', data=height_y_pol, compression="gzip")

    # A group to store the A-Scan measurements '/A-Scan'
    asc_grp = output_file.create_group('/A-Scan')

    # A-Scan values are stored in data-sets under the '/A-Scan' group
    if freq_dom:
        if real_part_x_pol:
            asc_grp.create_dataset('Re{S21 x-pol}', (len(real_part_x_pol), len(real_part_x_pol[0])), dtype='f4',
                               data=real_part_x_pol, compression="gzip")
        if imag_part_x_pol:
            asc_grp.create_dataset('Im{S21 x-pol}', (len(imag_part_x_pol), len(imag_part_x_pol[0])), dtype='f4',
                               data=imag_part_x_pol, compression="gzip")
        if real_part_y_pol:
            asc_grp.create_dataset('Re{S21 y-pol}', (len(real_part_y_pol), len(real_part_y_pol[0])), dtype='f4',
                               data=real_part_y_pol, compression="gzip")
        if imag_part_y_pol:
            asc_grp.create_dataset('Im{S21 y-pol}', (len(imag_part_y_pol), len(imag_part_y_pol[0])), dtype='f4',
                               data=imag_part_y_pol, compression="gzip")
    if time_dom:
        if real_part_x_pol:
            asc_grp.create_dataset('Re{A-Scan x-pol}', (len(real_part_x_pol), len(real_part_x_pol[0])), dtype='f4',
                               data=real_part_x_pol, compression="gzip")
        if imag_part_x_pol:
            asc_grp.create_dataset('Im{A-Scan x-pol}', (len(imag_part_x_pol), len(imag_part_x_pol[0])), dtype='f4',
                               data=imag_part_x_pol, compression="gzip")
        if real_part_y_pol:
            asc_grp.create_dataset('Re{A-Scan y-pol}', (len(real_part_y_pol), len(real_part_y_pol[0])), dtype='f4',
                               data=real_part_y_pol, compression="gzip")
        if imag_part_y_pol:
            asc_grp.create_dataset('Im{A-Scan y-pol}', (len(imag_part_y_pol), len(imag_part_y_pol[0])), dtype='f4',
                               data=imag_part_y_pol, compression="gzip")

def store_c_scan_gprmax_dot_h5(scan_files, output_file):
    output_file.close() # Closes the output file before creating an exception
    # Because this extension has not been released by gprMax is not yet supported
    raise Exception(".h5 A-Scan files are not yet supported")

def store_c_scan_files(folder, title = "C-Scan"):
    """Creates a .h5 file to store the the C-Scan in a 3D matrix of dimensions max(col),max(row),len(amplitude)
    Args:
        folder (string): Route for the folder/directory with the A-Scan files
        (for gprMax A-Scans, the .in file should also be in this folder/directory)
        title (string): Title of the output C-Scan fle
    """

    # Reads the name of the A-Scan files in the folder/directory
    scan_files = read_file_names(folder)

    # Creates an output .h5 file where the A-Scans will be merged to
    path = folder + '/C_Scans/'
    if not os.path.isdir(path):
        os.mkdir(path)
    output_file_name = path + title + '.h5'
    output_file = h5py.File(output_file_name, 'w')

    # Detects the extension of the original A-Scan files
    _, extension = os.path.splitext(scan_files[0])

    # Creates and populates attributes of the C-Scan file
    output_file.attrs['Title'] = title # Title of the output file
    output_file.attrs['Total Amount of A-Scans'] = len(scan_files) # Total amount of A-Scans in the output file
    output_file.attrs['Original extension of A-Scans'] = extension # Original extension of A-Scans in the output file

    # Note: The total amount of A-Scans is not necessarily the same as the surveyed points. When dual polarization scans
    # are done, the total amount of A-Scans will be twice as many surveyed points.

    if extension == ".out":
        # The folder where the A-Scan files are stored (most of the time this folder has the gprMax input file too)
        # is given to the following function as a parameter to retrieve the source polarization and height of the
        # antennas in reference to the ground surface
        polarization, height, average_h_flag = store_c_scan_gprmax_input(folder)
        # The A-Scan and output files are processed by the following function to add all of the missing information
        # into the output file
        store_c_scan_gprmax_dot_out(scan_files, output_file, polarization, height, average_h_flag)
    elif extension == ".csv":
        # The A-Scan and output files are processed by the following function to add all of the missing information
        # into the output file
        store_c_scan_gpr(scan_files, output_file)
    elif extension == ".h5":
        # The A-Scan and output files are processed by the following function to add all of the missing information
        # into the output file
        store_c_scan_gprmax_dot_h5(scan_files, output_file)

    # Output file is closed with all the information written in it
    output_file.close()

if __name__ == '__main__':
    # Prompts the user with a basic interface to select a folder/directory with the A-Scan file to merge
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(parent=root, initialdir=os.getcwd())
    root.destroy()

    # Generates the merged file with an output title
    output_file_title = 'C_Scan_default_title'
    store_c_scan_files(directory, title=output_file_title)

    sys.exit()