import os
import h5py
import numpy as np
from mayavi import mlab
import tkinter as tk
from tkinter import filedialog


def plot_c_scan_from_merged_file(merged_file_name, polarization='x', amp=0):
    """Function that reads a merged file and calls the C-Scan plotting function
    Args:
      merged_file_name (string): Name of the merged file.
      polarization (string): Identifier of the polarization to be plotted in the C-Scan. If 'x' or 'y' is received, just
      the corresponding polarization B-Scans are plotted. Other entries plot C-Scans for both polarizations.
      (Default = 'x')
      amp (float): Amplitude to be taken as maximum and minimum for the C-Scan colorbar. If zero is received, the
      function will find the range within the A-Scan amplitudes of the merged file. (Default = 0)
    """
    # Merged file is opened into data_frame variable
    print(merged_file_name)
    data_frame = h5py.File(merged_file_name, 'r')
    # Identifiers are set into lower case
    polarization = polarization.lower()
    # Title for the C-Scan figure
    title = data_frame.attrs['Title'] + ' C-Scan for ' + polarization + '-polarization'
    # Time-domain lower and upper limits are retrieved
    t0 = data_frame['Time'].attrs['t0']
    tf = data_frame['Time'].attrs['tf']
    qt = int(data_frame['Time'].attrs['q'])
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

    if polarization == 'x' or polarization == 'y':
        # Creates numpy 3D array for storing C-Scan data
        c_scan_scalars = np.zeros([qx, qy, qt])
    else:
        data_frame.close()
        raise Exception("Can only plot the C-Scan of one polarization at a time. Please specify if x or y.")

    for i in range(0, qx):
        # Indexes used to retrieve individual planes of the C-Scan are calculated
        index_0 = i * qy
        index_f = (i + 1) * qy

        if polarization == 'x':
            # C-Scan data is retrieved from the merged file
            c_scan_scalars[i, :, :] = data_frame['A-Scan/Re{A-Scan x-pol}'][index_0:index_f][:]
        else:
            # C-Scan data is retrieved from the merged file
            c_scan_scalars[i, :, :] = data_frame['A-Scan/Re{A-Scan y-pol}'][index_0:index_f][:]

    # Grid with the domain points is created. Time axis is scaled to be within the same orders of magnitude as x and y.
    x, y, z = np.mgrid[x0:xf:qx * 1j, y0:yf:qy * 1j, tf * 10 ** 8:t0:qt * 1j]

    # Labels for the horizontal and vertical axes are set
    x_label = 'x [m]'
    y_label = 'y [m]'
    v_label = 't [x10 ns]'

    # Figure is created
    mlab.figure(figure=title, size=(1100, 800))
    # Volume slice type plot is added to the figure
    if amp != 0:
        mlab.volume_slice(x, y, z, np.abs(c_scan_scalars), opacity=0.4, reset_zoom=True, vmax=amp, vmin=-amp)
    else:
        mlab.volume_slice(x, y, z, np.abs(c_scan_scalars), opacity=0.4, reset_zoom=True)
    # Options for the colorbar and axes are set
    cb1 = mlab.colorbar(orientation="vertical", nb_labels=5)
    cb1.scalar_bar.unconstrained_font_size = True
    cb1.label_text_property.font_size = 10
    cb1.label_text_property.bold = False
    cb1.label_text_property.italic = False
    ax = mlab.axes(xlabel=x_label, ylabel=y_label, zlabel=v_label)
    ax.label_text_property.font_size = 1
    ax.title_text_property.font_size = 1
    # Outline for the volume slice is added to the figure
    mlab.outline()
    # Title is added to the figure
    mlab.title(title, size=0.2, height=0)
    # Contour type plot is added to the figure
    if amp != 0:
        mlab.contour3d(x, y, z, c_scan_scalars, opacity=0.4, reset_zoom=True, vmax=amp, vmin=-amp, contours=10)
    else:
        mlab.contour3d(x, y, z, c_scan_scalars, opacity=0.4, reset_zoom=True, contours=10)
    # Figure is displayed
    mlab.show()

    # Data frame of the .h5 file is closed
    data_frame.close()


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    file = filedialog.askopenfilename(parent=root, initialdir=os.getcwd())
    root.destroy()
    # C-Scans of the merged file are plotted
    plot_c_scan_from_merged_file(file)
