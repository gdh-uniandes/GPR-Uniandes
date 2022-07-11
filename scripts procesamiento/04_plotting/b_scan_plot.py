import os
import h5py
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
def plot_function(b_scan, v_dim0, v_dimf, h_dim0, h_dimf, title, hlabel, vlabel, minimum, maximum):
    """Function for plotting the B-Scan received by parameter
    Args:
      b_scan (nested-list float): Amplitudes of the B-Scan.
      v_dim0 (float): Value of the lower limit of the vertical axis.
      v_dimf (float): Value of the upper limit of the vertical axis.
      h_dim0 (float): Value of the lower limit of the horizontal axis.
      h_dimf (float): Value of the upper limit of the horizontal axis.
      title (string): Title to be assigned to the B-Scan plot.
      hlabel (string): Label to be assigned to the horizontal axis.
      vlabel (string): Label to be assigned to the vertical axis.
      minimum (float): Minimum amplitude of the B-Scans to be plotted
      maximum (float): Maximum amplitude of the B-Scans to be plotted
    """
    # Figure for the plot is opened
    figure = plt.figure(title)
    # Plot style is imshow() the image parameter is the B-Scan and the extent is determined by the dimensions of the
    # vertical and horizontal axes. Interpolation, aspect, colormap, and amplitude range is also sent as parameter
    plt.imshow(b_scan.T, extent=[h_dim0, h_dimf, v_dim0, v_dimf], interpolation='nearest',
               aspect='auto', cmap='seismic', vmin=minimum, vmax=maximum)
    # Labels are added to the plot
    plt.xlabel(hlabel)
    plt.ylabel(vlabel)
    plt.title(title)
    # Grid is added to the plot
    ax = figure.gca()
    ax.grid(which='both', axis='both', linestyle='-.')
    # Colormap is made visible
    plt.colorbar()
    # The plt.show() command should be executed after the current function to display the plots. This command is not
    # included inside the current function in case several simultaneous plots are needed

def plot_b_scan_from_merged_file(merged_file_name, horizontal_axis = 'x', plane_num = 0, polarization = 'x', amp = 0):
    """Function that reads a merged file and calls the B-Scan plotting function with the proper arguments
    Args:
      merged_file_name (string): Name of the merged file.
      horizontal_axis (string): Identifier of the horizontal axis to be plotted in the B-Scan. (Default = 'x')
      plane_num (int): Optional argument to plot the B-Scan of a single plane from the merged file. By default all
      possible planes are plotted. (Default = 0)
      polarization (string): Identifier of the polarization to be plotted in the B-Scan. If 'x' or 'y' is received, just
      the corresponding polarization B-Scans are plotted. Other entries plot B-Scans for both polarizations.
      (Default = 'x')
      amp (float): Amplitude to be taken as maximum and minimum for the B-Scan colorbar. If zero is received, the
      function will find the range within the A-Scan amplitudes of the merged file. (Default = 0)
    """
    # Merged file is opened into data_frame variable
    data_frame = h5py.File(merged_file_name, 'r')

    # Time-domain lower and upper limits are retrieved
    t0 = data_frame['Time'].attrs['t0']
    tf = data_frame['Time'].attrs['tf']
    # x- and y-axis lower limits, upper limits and step are retrieved
    x0 = data_frame['Position'].attrs['x0']
    dx = data_frame['Position'].attrs['dx']
    xf = data_frame['Position'].attrs['xf']
    y0 = data_frame['Position'].attrs['y0']
    dy = data_frame['Position'].attrs['dy']
    yf = data_frame['Position'].attrs['yf']
    # Amount of steps over each axis is calculated. Operation rounds up the division result as needed
    qx = int(round((xf - x0) / dx + 1))
    qy = int(round((yf - y0) / dy + 1))
    # Identifiers are set into lower case
    horizontal_axis = horizontal_axis.lower()
    polarization = polarization.lower()
    # Labels for the horizontal and vertical axes are set
    h_label = horizontal_axis + ' [m]'
    v_label = 'Time [s]'
    # Minimum and maximum amplitudes of the merged file are set for each polarization
    min_x_pol = - amp
    max_x_pol = amp
    min_y_pol = - amp
    max_y_pol = amp
    if amp == 0:
        if polarization != 'y':
            min_x_pol = min([val for sublist in data_frame['A-Scan/Re{A-Scan x-pol}'] for val in sublist])
            max_x_pol = max([val for sublist in data_frame['A-Scan/Re{A-Scan x-pol}'] for val in sublist])
        if polarization != 'x':
            min_y_pol = min([val for sublist in data_frame['A-Scan/Re{A-Scan y-pol}'] for val in sublist])
            max_y_pol = max([val for sublist in data_frame['A-Scan/Re{A-Scan y-pol}'] for val in sublist])
    # Initializes B-Scans
    b_scan_x = []
    b_scan_y = []
    # The set horizontal axis is verified and the script proceeds accordingly
    if horizontal_axis == 'y':
        # Checks whether a plane number is given
        if plane_num != 0:
            # Indexes used to retrieve individual B-Scans are calculated
            index_0 = (plane_num - 1) * qy
            index_f = plane_num * qy - 1
            # Polarization to be plotted is checked
            if polarization == 'x':
                # Title for the B-Scan plot is set
                title = 'B-Scan x-polarization plane #' + str(plane_num)
                title = 'B-Scan #' + str(plane_num) + '- landmine buried at 90 mm (raw)'
                # B-Scan data is retrieved from the merged file
                b_scan_x = data_frame['A-Scan/Re{A-Scan x-pol}'][index_0:index_f][:]
                # B-Scan data is sent to plot_function to be plotted
                plot_function(b_scan_x, tf, t0, y0, yf, title, h_label, v_label, min_x_pol, max_x_pol)

            elif polarization == 'y':
                # Title for the B-Scan plot is set
                title = 'B-Scan y-polarization plane #' + str(plane_num)
                # B-Scan data is retrieved from the merged file
                b_scan_y = data_frame['A-Scan/Re{A-Scan y-pol}'][index_0:index_f][:]
                # B-Scan data is sent to plot_function to be plotted
                plot_function(b_scan_y, tf, t0, y0, yf, title, h_label, v_label, min_y_pol, max_y_pol)

            else:
                # Title for the B-Scan plot is set
                title = 'B-Scan x-polarization plane #' + str(plane_num)
                # B-Scan data is retrieved from the merge
                b_scan_x = data_frame['A-Scan/Re{A-Scan x-pol}'][index_0:index_f][:]
                # B-Scan data is sent to plot_function to be plotted
                plot_function(b_scan_x, tf, t0, y0, yf, title, h_label, v_label, min_x_pol, max_x_pol)

                # Title for the B-Scan plot is set
                title = 'B-Scan y-polarization plane #' + str(plane_num)
                # B-Scan data is retrieved from the merge
                b_scan_y = data_frame['A-Scan/Re{A-Scan y-pol}'][index_0:index_f][:]
                # B-Scan data is sent to plot_function to be plotted
                plot_function(b_scan_y, tf, t0, y0, yf, title, h_label, v_label, min_y_pol, max_y_pol)
            # Plot is displayed
            plt.show()
        else:
            # If plane number is not specified, all possible B-Scans are plotted
            for i in range(1, qx + 1):
                # Indexes used to retrieve individual B-Scans are calculated
                index_0 = (i - 1) * qy
                index_f = i * qy
                # Polarization to be plotted is checked
                if polarization == 'x':
                    # Title for the B-Scan plot is set
                    title = 'B-Scan x-polarization plane #' + str(i)
                    # B-Scan data is retrieved from the merged file
                    b_scan_x = data_frame['A-Scan/Re{A-Scan x-pol}'][index_0:index_f][:]
                    # B-Scan data is sent to plot_function to be plotted
                    plot_function(b_scan_x, tf, t0, y0, yf, title, h_label, v_label, min_x_pol, max_x_pol)

                elif polarization == 'y':
                    # Title for the B-Scan plot is set
                    title = 'B-Scan y-polarization plane #' + str(i)
                    # B-Scan data is retrieved from the merged file
                    b_scan_y = data_frame['A-Scan/Re{A-Scan y-pol}'][index_0:index_f][:]
                    # B-Scan data is sent to plot_function to be plotted
                    plot_function(b_scan_y, tf, t0, y0, yf, title, h_label, v_label, min_y_pol, max_y_pol)

                else:
                    # Title for the B-Scan plot is set
                    title = 'B-Scan x-polarization plane #' + str(plane_num)
                    # B-Scan data is retrieved from the merged file
                    b_scan_x = data_frame['A-Scan/Re{A-Scan x-pol}'][index_0:index_f][:]
                    # B-Scan data is sent to plot_function to be plotted
                    plot_function(b_scan_x, tf, t0, y0, yf, title, h_label, v_label, min_x_pol, max_x_pol)

                    # Title for the B-Scan plot is set
                    title = 'B-Scan y-polarization plane #' + str(plane_num)
                    # B-Scan data is retrieved from the merged file
                    b_scan_y = data_frame['A-Scan/Re{A-Scan y-pol}'][index_0:index_f][:]
                    # B-Scan data is sent to plot_function to be plotted
                    plot_function(b_scan_y, tf, t0, y0, yf, title, h_label, v_label, min_y_pol, max_y_pol)
                # Plot is displayed
                plt.show()
    else:
        # Checks whether a plane number is given
        if plane_num != 0:
            # Indexes used to retrieve individual B-Scans are calculated
            indxs = [num - 1 for num in range(plane_num, qx * qy + plane_num) if (num - plane_num % qx) % qy == 0]
            # Polarization to be plotted is checked
            if polarization == 'x':
                # Title for the B-Scan plot is set
                title = 'B-Scan #' + str(plane_num) + '- x-direction empty box (removed)'
                # B-Scan data is retrieved from the merged file
                b_scan_x = data_frame['A-Scan/Re{A-Scan x-pol}'][indxs][:]
                # B-Scan data is sent to plot_function to be plotted
                plot_function(b_scan_x, tf, t0, y0, yf, title, h_label, v_label, min_x_pol, max_x_pol)

            elif polarization == 'y':
                # Title for the B-Scan plot is set
                title = 'B-Scan y-polarization plane #' + str(plane_num)
                # B-Scan data is retrieved from the merged file
                b_scan_y = data_frame['A-Scan/Re{A-Scan y-pol}'][indxs][:]
                # B-Scan data is sent to plot_function to be plotted
                plot_function(b_scan_y, tf, t0, y0, yf, title, h_label, v_label, min_y_pol, max_y_pol)

            else:
                # Title for the B-Scan plot is set
                title = 'B-Scan x-polarization plane #' + str(plane_num)
                # B-Scan data is retrieved from the merged file
                b_scan_x = data_frame['A-Scan/Re{A-Scan x-pol}'][indxs][:]
                # B-Scan data is sent to plot_function to be plotted
                plot_function(b_scan_x, tf, t0, y0, yf, title, h_label, v_label, min_x_pol, max_x_pol)

                # Title for the B-Scan plot is set
                title = 'B-Scan y-polarization plane #' + str(plane_num)
                # B-Scan data is retrieved from the merged file
                b_scan_y = data_frame['A-Scan/Re{A-Scan y-pol}'][indxs][:]
                # B-Scan data is sent to plot_function to be plotted
                plot_function(b_scan_y, tf, t0, y0, yf, title, h_label, v_label, min_y_pol, max_y_pol)

            # Plot is displayed
            plt.show()
        else:
            for i in range(1, qy + 1):
                # Indexes used to retrieve individual B-Scans are calculated
                indxs = [num - 1 for num in range(i, qx * qy + i) if (num - i % qx) % qy == 0]
                # Polarization to be plotted is checked
                if polarization == 'x':
                    # Title for the B-Scan plot is set
                    title = 'B-Scan x-polarization plane #' + str(i)
                    # B-Scan data is retrieved from the merged file
                    b_scan_x = data_frame['A-Scan/Re{A-Scan x-pol}'][indxs][:]
                    # B-Scan data is sent to plot_function to be plotted
                    plot_function(b_scan_x, tf, t0, y0, yf, title, h_label, v_label, min_x_pol, max_x_pol)

                elif polarization == 'y':
                    # Title for the B-Scan plot is set
                    title = 'B-Scan y-polarization plane #' + str(i)
                    # B-Scan data is retrieved from the merged file
                    b_scan_y = data_frame['A-Scan/Re{A-Scan y-pol}'][indxs][:]
                    # B-Scan data is sent to plot_function to be plotted
                    plot_function(b_scan_y, tf, t0, y0, yf, title, h_label, v_label, min_y_pol, max_y_pol)

                else:
                    # Title for the B-Scan plot is set
                    title = 'B-Scan x-polarization plane #' + str(plane_num)
                    # B-Scan data is retrieved from the merged file
                    b_scan_x = data_frame['A-Scan/Re{A-Scan x-pol}'][indxs][:]
                    # B-Scan data is sent to plot_function to be plotted
                    plot_function(b_scan_x, tf, t0, y0, yf, title, h_label, v_label, min_x_pol, max_x_pol)

                    # Title for the B-Scan plot is set
                    title = 'B-Scan y-polarization plane #' + str(plane_num)
                    # B-Scan data is retrieved from the merged file
                    b_scan_y = data_frame['A-Scan/Re{A-Scan y-pol}'][indxs][:]
                    # B-Scan data is sent to plot_function to be plotted
                    plot_function(b_scan_y, tf, t0, y0, yf, title, h_label, v_label, min_y_pol, max_y_pol)

                # Plot is displayed
                plt.show()

    # data_frame is closed
    data_frame.close()
    # Returns the last B-Scans that were plotted
    return b_scan_x, b_scan_y

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    file = filedialog.askopenfilename(parent=root, initialdir=os.getcwd())
    root.destroy()
    # B-Scans of the merged file are plotted
    plot_b_scan_from_merged_file(file, horizontal_axis='y', amp=0.0065, plane_num=70)