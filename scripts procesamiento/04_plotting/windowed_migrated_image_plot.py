import h5py
import numpy as np
from mayavi import mlab

def plot_migrated_image_from_merged_file(migrated_image_file_name, z_ini, z_end):
    """Function that reads a file and plots the migrated image
    Args:
      migrated_image_file_name (string): Name of the file with the migrated image.
    """
    # File is opened into data_frame variable
    data_frame = h5py.File(migrated_image_file_name, 'r')
    # Title for the migrated image figure
    title = data_frame.attrs['Title']
    # x-, y- and z-axis lower limits, upper limits and amount of measurements are read
    x0 = data_frame['Position'].attrs['x0']
    xf = data_frame['Position'].attrs['xf']
    y0 = data_frame['Position'].attrs['y0']
    yf = data_frame['Position'].attrs['yf']
    z0 = data_frame['Position'].attrs['z0']
    zf = data_frame['Position'].attrs['zf']
    qx = data_frame['Position'].attrs['qx']
    qy = data_frame['Position'].attrs['qy']
    qz = data_frame['Position'].attrs['qz']
    # Reads the migrated image
    mi = data_frame['MigratedImage/Image'][z_ini:z_end][:][:]
    # Data frame is closed
    data_frame.close()
    # Calculate new z-axis
    z = np.linspace(zf, z0, qz)
    # Grid with the domain points is created. Time axis is scaled to be within the same orders of magnitude as x and y.
    xg, yg, zg = np.mgrid[x0:xf:qx * 1j, y0:yf:qy * 1j, z[z_ini]:z[z_end]:z_end-z_ini * 1j]
    # Labels for the horizontal and vertical axes are set
    x_label = 'x [m]'
    y_label = 'y [m]'
    v_label = 'z [m]'
    # Figure is created
    mlab.figure(figure=title, size=(1100, 800))
    # Volume slice type plot is added to the figure
    mlab.volume_slice(xg, yg, zg, mi, opacity=0.4, reset_zoom=True)
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
    mlab.contour3d(xg, yg, zg, mi, opacity=0.4, reset_zoom=True, contours=25)
    # Figure is displayed
    mlab.show()
    

if __name__ == '__main__':
    # Time-domain merged file with C-Scan to be plotted is specified. Replace route with the route to the desired file:
    file = 'D:/Daniel/Documents/02_mediciones_lab/03_esfera_metalica_7mm_350_350_110mm/02_20213111912/C_Scans/migration_er2.58.h5'
    # Define z-caxis indexes for window
    z_ini = 5
    z_end = 15
    # C-Scans of the merged file are plotted
    plot_migrated_image_from_merged_file(file, z_ini - 1, z_end - 1)