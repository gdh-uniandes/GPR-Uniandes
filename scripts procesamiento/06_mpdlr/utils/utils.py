from typing import Tuple, Optional

import h5py
import logging

import numpy as np
import matplotlib.pyplot as plt

from scipy import signal, interpolate
from sklearn.cluster import DBSCAN

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def get_output_data(filename, rxnumber, rxcomponent):
    """Gets B-scan output data from a model. Taken from gprMax
    Args:
        filename (string): Filename (including path) of output file.
        rxnumber (int): Receiver output number.
        rxcomponent (str): Receiver output field/current component.
    Returns:
        outputdata (array): Array of A-scans, i.e. B-scan data.
        dt (float): Temporal resolution of the model.
    """

    # Open output file and read some attributes
    f = h5py.File(filename, 'r')
    nrx = f.attrs['nrx']
    dt = f.attrs['dt']

    # Check there are any receivers
    if nrx == 0:
        raise Exception('No receivers found in {}'.format(filename))

    path = '/rxs/rx' + str(rxnumber) + '/'
    availableoutputs = list(f[path].keys())

    # Check if requested output is in file
    if rxcomponent not in availableoutputs:
        raise Exception('{} output requested to plot, but the available output for receiver 1 is {}'.format(rxcomponent,
                                                                                                            ', '.join(
                                                                                                                availableoutputs)))

    outputdata = f[path + '/' + rxcomponent]
    outputdata = np.array(outputdata)
    f.close()

    return outputdata, dt


def read_c_scan(filename: str, polarization: str = 'x') -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Reads an .h5 file containing a time domain C-Scan and gets the data in an array.
    Args:
        filename (str): Filename (or path) of the .h5 file.
        polarization (sr): Polarization of the data.

    Returns:
        c_scan (ndarray): C-Scan of shape (q_x, q_y, q_t)
        x (ndarray): x-axis.
        y (ndarray): y-axis.
        t (ndarray): t-axis.

    """
    if polarization not in ['x', 'y']:
        raise ValueError(f"Value {polarization} not valid. Should be : x or y")

    data_frame = h5py.File(filename, 'r')

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

    # Axis ndarray created
    x = np.linspace(x0, xf, qx)
    y = np.linspace(y0, yf, qy)
    t = np.linspace(t0, tf, qt)

    c_scan = np.zeros((qx, qy, qt), dtype=np.cfloat)

    for i in range(0, qx):
        # Indexes used to retrieve individual planes of the C-Scan are calculated
        index_0 = i * qy
        index_f = (i + 1) * qy
        c_scan[i, :, :] = data_frame[f'A-Scan/Re{{A-Scan {polarization}-pol}}'][index_0:index_f][:] \
                          + 1j * data_frame[f'A-Scan/Im{{A-Scan {polarization}-pol}}'][index_0:index_f][:]

    return c_scan, x, y, t


def plot_mine_map(x, y, mine_map):
    """
    Plots a probability map
    :param x: x-axis
    :param y: y-axis
    :param mine_map: ndarray with probabilities
    :return: None
    """
    plt.figure(figsize=(10, 10))
    plt.grid(False)
    plt.pcolor(x, y, mine_map, shading='auto', cmap='YlGnBu')
    #plt.colorbar()
    plt.clim(0, np.max(mine_map))
    plt.xlabel('x')
    plt.ylabel('y')
    plt.show()
