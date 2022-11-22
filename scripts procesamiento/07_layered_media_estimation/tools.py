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


def traces_coherency(traces: np.ndarray, offsets: np.ndarray, time: np.ndarray, velocity: np.ndarray) -> np.ndarray:
    """
    Gets the velocity spectrum from sum of cross correlation for CMP data.

    Args:
        traces (ndarray): CMP data of shape (q_x, q_t)
        offsets (ndarray): Offset of the CMP data.
        time (ndarray):  Time-axis of CMP data.
        velocity (ndarray):  Trial velocities

    Returns:
        coherency (ndarray): Velocity spectrum of shape (q_t, q_v)

    """

    n_offset = offsets.size
    z = velocity[np.newaxis, :] * time[:, np.newaxis] / 2
    t_z = np.sqrt(offsets[:, np.newaxis, np.newaxis] ** 2 + 4 * z[np.newaxis, :, :] ** 2) / velocity[np.newaxis,
                                                                                            np.newaxis, :]
    f = interpolate.interp1d(time, signal.hilbert(traces), kind='linear', axis=-1, fill_value='extrapolate')
    f = f(t_z)

    coherency = np.zeros((time.size, velocity.size))

    for v_idx, v in enumerate(velocity):
        for tau_idx, tau in enumerate(time):
            cc = 0
            for i in range(n_offset - 1):
                for j in range(i, n_offset):
                    cc += np.real(f[i, i, tau_idx, v_idx]) * np.real(f[j, j, tau_idx, v_idx]) + np.imag(
                        f[i, i, tau_idx, v_idx]) * np.imag(f[j, j, tau_idx, v_idx])

            coherency[tau_idx, v_idx] = cc

    return coherency


def find_coherency_picks(coherency: np.ndarray, t: np.ndarray, velocity: np.ndarray):
    """
    Find coherency picks of velocity spectrum using DBSCAN for those values that are above 90% of distribution.
    Args:
        coherency (ndarray):
        t (ndarray):
        velocity (ndarray):

    Returns:

    """
    th = np.quantile(coherency, 0.90)
    th_idx = np.where(coherency >= th)

    X = np.column_stack((th_idx[0], th_idx[1]))
    dbscan = DBSCAN(eps=2, min_samples=10).fit(X)

    n_clusters = np.max(dbscan.labels_) + 1
    log.info(f"Number of clusters found: {n_clusters}")
    max_cc_idx = np.zeros((n_clusters, 2), dtype=int)
    for i in range(n_clusters):
        cluster_idx = X[dbscan.labels_ == i]
        max_cluster_cc_idx = np.where(
            coherency == np.amax(coherency[cluster_idx[:, 0], cluster_idx[:, 1]]))
        max_cc_idx[i, :] = np.array([max_cluster_cc_idx[0][0], max_cluster_cc_idx[1][0]])

    max_cc_idx = max_cc_idx[max_cc_idx[:, 0].argsort()]

    max_t = np.zeros(n_clusters)
    max_v = np.zeros(n_clusters)
    for i in range(n_clusters):
        max_t[i], max_v[i] = t[max_cc_idx[i, 0]], velocity[max_cc_idx[i, 1]]

    return max_t, max_v


def layer_parameter_estimation(traces: np.ndarray, offsets: np.ndarray, t: np.ndarray, velocity: np.ndarray,
                               coherency: Optional[np.ndarray] = None) -> Tuple[list, list]:
    """
    Estimates permittivity and thickness of two layered media using CMP data.
    Args:
        traces (ndarray): CMP data of shape (q_x, q_t)
        offsets (ndarray): Antenna offsets of CMP data.
        t (ndarray): Time-axis of CMP data.
        velocity (ndarray): Trial velocities.
        coherency (ndarray): Precalculated velocity spectrum if not given it will be calculated

    Returns:
        permittivity (ndarray): Estimated permittivity of each layer
        thickness (ndarray): Estimated thickness of each layer.

    """
    if coherency is None:
        coherency = traces_coherency(traces, offsets, t, velocity)

    max_t, max_v = find_coherency_picks(coherency, t, velocity)

    t_1, v_1 = max_t[1], max_v[1]
    t_2, v_2 = max_t[2], max_v[2]
    log.info(f"First picked time {t_1 * 1e9:.4f} ns, and picked velocity: {v_1 * 1e-9:.4f} m/ns")
    log.info(f"Second picked time {t_2 * 1e9:.4f} ns, and picked velocity: {v_2 * 1e-9:.4f} m/ns")

    v_int = np.sqrt((v_2 ** 2 * t_2 - v_1 ** 2 * t_1) / (t_2 - t_1))

    e_r_1, z_1 = (3e8 / v_1) ** 2, v_1 * t_1 / 2
    e_r_2, z_2 = (3e8 / v_int) ** 2, v_int * (t_2 - t_1) / 2

    permittivities = np.array([e_r_1, e_r_2])
    thicknesses = np.array([z_1, z_2])

    return permittivities, thicknesses


def plot_cmp_profile(traces: np.ndarray, offsets: np.ndarray, time: np.ndarray):
    """
    Plot CMP profile
    Args:
        traces (ndarray): CMP data of shape (q_x, q_t)
        offsets (ndarray): Antenna offsets of CMP data.
        time (ndarray): Time-axis of CMP data.

    Returns:

    """
    fig, ax = plt.subplots(figsize=(10, 10))
    plot_1 = ax.pcolor(offsets * 1e2, time * 1e9, traces.swapaxes(0, 1), cmap='seismic')
    ax.invert_yaxis()
    ax.set_xlabel("Offset [cm]")
    ax.set_ylabel("Time [ns]")
    fig.colorbar(plot_1, ax=ax)


def plot_velocity_spectrum(coherency: np.ndarray, velocity: np.ndarray, time: np.ndarray, markers: list[tuple]):
    """

    Args:
        coherency (ndarray): Velocity spectrum of shape (q_t, q_v)
        velocity (ndarray): Velocity-axis.
        time (ndarray): Time-axis.
        markers (list[tuple]): List of time, velocity tuples.

    Returns:

    """
    fig, ax = plt.subplots(figsize=(10, 10))
    plot_1 = ax.pcolor(velocity * 1e-9, time * 1e9, coherency, cmap='jet')
    for (t, v) in markers:
        ax.plot(v * 1e-9, t * 1e9, 'w+', ms=2)
    ax.invert_yaxis()
    ax.set_xlabel("Velocity [m/ns]")
    ax.set_ylabel("Time [ns]")
    fig.colorbar(plot_1, ax=ax)


def print_estimation_results(true_permittivities: np.ndarray, est_permittivities: np.ndarray, true_thicknesses: np.ndarray, est_thicknesses: np.ndarray):
    """
    Prints results of estimation of permittivity and thickness of two layered media
    Args:
        true_permittivities (ndarray): True permittivity for each layer.
        est_permittivities (ndarray): Estimated permittivity for each layer.
        true_thicknesses (ndarray): True thickness for each layer.
        est_thicknesses (ndarray): Estimated thickness for each layer.

    Returns:

    """
    permittivity_error = np.abs(est_permittivities - true_permittivities) / true_permittivities
    thicknesses_error = np.abs(est_thicknesses - true_thicknesses) / true_thicknesses
    print()
    print("Layer 1")
    print(
        f"True permittivity is {true_permittivities[0]:.2f}, estimated was {est_permittivities[0]:.2f}. Error: {permittivity_error[0]:.2%}")
    print(
        f"True thickness is {true_thicknesses[0]:.2f}, estimated was {est_thicknesses[0]:.2f}. Error: {thicknesses_error[0]:.2%}")
    print()
    print("Layer 2")
    print(
        f"True permittivity is {true_permittivities[1]:.2f}, estimated was {est_permittivities[1]:.2f}. Error: {permittivity_error[1]:.2%}")
    print(
        f"True thickness is {true_thicknesses[1]:.2f}, estimated was {est_thicknesses[1]:.2f}. Error: {thicknesses_error[1]:.2%}")
