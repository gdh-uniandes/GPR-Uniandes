import os
from typing import Union, Tuple, Optional

import h5py
import time
import argparse
import numpy as np
import itertools
import multiprocessing as mp

from numba import jit


@jit(nopython=True)
def transmission_angles_2d(er, h, xp, zp, xc):
    """Calculates incidence angles with Snell's law
    Args:
      er (float): Ground apparent relative permittivity.
      h (float): Height of the antennas from ground [m].
      xp (float): horizontal-coordinate of the point in ground subsurface.
      zp (float): z-coordinate of the point in ground subsurface.
      xc (float): horizontal-coordinate of the antenna location.
    """
    # Creates arrays for all the possible transmission angles
    possible_theta_g = np.linspace(0, np.pi / 2, 2 ** 8)
    possible_theta_a = np.arcsin(np.minimum(np.sqrt(er) * np.sin(possible_theta_g), np.asarray([1])))
    # Looks for the solution of the transmission angle equation
    min_index = np.argmin(np.abs(np.abs(xc - xp) - zp * np.tan(possible_theta_g) - h * np.tan(possible_theta_a)))
    # Returns the found transmission angles
    return possible_theta_a[min_index], possible_theta_g[min_index]

@jit(nopython=True)
def transmission_angles_3d(er, h, xp, yp, zp, xc, yc):
    """Calculates incidence angles with Snell's law
    Args:
      er (float): Ground apparent relative permittivity.
      h (float): Height of the antennas from ground [m].
      xp (float): horizontal-coordinate of the point in ground subsurface.
      zp (float): z-coordinate of the point in ground subsurface.
      xc (float): horizontal-coordinate of the antenna location.
    """
    # Creates arrays for all the possible transmission angles
    possible_theta_g = np.linspace(0, np.pi / 2, 2 ** 8)
    possible_theta_a = np.arcsin(np.minimum(np.sqrt(er) * np.sin(possible_theta_g), np.asarray([1])))
    # Looks for the solution of the transmission angle equation
    min_index = np.argmin(np.abs(np.sqrt((xp-xc)**2 +(yp-yc)**2) - zp * np.tan(possible_theta_g) - h * np.tan(possible_theta_a)))
    # Returns the found transmission angles
    return possible_theta_a[min_index], possible_theta_g[min_index]


def kirchhoff_migration_3d(c_scan, h_ant, er, t0, tf, dt, x0, xf, qx, y0, yf, qy, z0, zf):
    """Algorithm for Kirchhoff 2D migration
    Args:
      conn (Pipe): Connection pipe with the calling function.
      b_scan (nested-list float): Amplitudes of the B-Scan (should be pre-processed first).
      h_ant (float): Height of the antennas from ground [m].
      er (float): Ground apparent relative permittivity.
      t0 (float): Initial time value [s].
      tf (float): Final time value [s].
      dt (float): Time step [s].
      x0 (float): Initial horizontal axis value [m].
      xf (float): Final horizontal axis value [m].
      qx (float): Amount of values over the horizontal axis.
      z0 (float): Initial z-axis value [m].
      zf (float): Final z-axis value [m].
    """
    # Speed of light constant definition and calculation of propagation velocity in ground
    c0 = 3e8  # [m/s]
    vp = c0 / np.sqrt(er)  # [m/s]
    # Creation of time and space arrays
    x = np.linspace(x0, xf, qx)
    y = np.linspace(y0, yf, qy)
    t = np.arange(t0, tf, dt)
    if len(t) != len(c_scan[0, 0]):
        if len(t) > len(c_scan[0, 0]):
            t = np.arange(t0, tf - dt, dt)
        else:
            t = np.arange(t0, tf + dt, dt)
    z = np.arange(z0, zf, dt * vp)
    # Calculate frequency domain array
    fs = 1 / dt
    f = np.linspace(-fs / 2, fs / 2, len(t))
    # Calculate half-derivative term and its multiplication with the B-Scan
    c_scan_f = np.fft.fftshift(np.fft.fft2(c_scan, axes=[0, 1]), axes=[0, 1])  # B-Scan in the frequency domain
    half_der = np.tile(1j * 2 * np.pi * f.T, (qx, qy, 1))  # Half derivative term
    d_c_scan = np.real(np.fft.ifft2(np.fft.ifftshift(half_der * c_scan_f, axes=0), axes=[0, 1]))  # Time domain expression
    # Create empty array for angles and integration kernel

    # Create empty matrix for the integral kernel
    #kernel = np.zeros((qx, qy, qx, qy, len(z)))
    migrated_image = np.zeros((qx, qy, len(z)))
    processes = [[[0 for k in range(0, len(z))] for j in range(0, qy)] for i in range(0, qx)]
    pool = mp.Pool(processes=os.cpu_count()-1)
    for (i, j, k) in itertools.product(range(0, qx), range(0, qy), range(0, len(z))):
        xp, yp, zp = x[i], y[j], z[k]
        #print(f"Migrating point ({i}, {j}, {k})")
        processes[i][j][k] = pool.apply_async(migrate_point_3d, args=(c0, d_c_scan, er, h_ant, qx, qy, t, vp, x, xp, y, yp, zp))
        #migrated_image[i, j, k] = migrate_point_3d(c0, d_c_scan, er, h_ant, qx, qy, t, vp, x, xp, y, yp, zp)

    for (i, j, k) in itertools.product(range(0, qx), range(0, qy), range(0, len(z))):
        migrated_image[i, j, k] = processes[i][j][k].get()
        print(f"Finished migrating point ({i}, {j}, {k})")

    return migrated_image


def migrate_point_3d(c0, d_c_scan, er, h_ant, qx, qy, t, vp, x, xp, y, yp, zp):

    theta_a_arr = np.zeros((len(x), len(y)))
    theta_g_arr = np.zeros((len(x), len(y)))
    for (l, m) in itertools.product(range(0, qx), range(0, qy)):
        xa, ya = x[l], y[m]
        theta_a, theta_g = transmission_angles_3d(er, h_ant, xp, yp, zp, xa, ya)
        theta_a_arr[l, m] = theta_a
        theta_g_arr[l, m] = theta_g
    r = h_ant * (1 / np.cos(theta_a_arr)) + zp * (1 / np.cos(theta_g_arr))
    t_e = 2 * (h_ant * (1 / np.cos(theta_a_arr)) / c0 + zp * (1 / np.cos(theta_g_arr)) / vp)
    time_diff = np.tile(t, (qx, qy, 1)) - np.repeat(t_e[:, :, np.newaxis], len(t), axis=2)
    coincidence_indexes = np.argmin(np.abs(time_diff), axis=2)
    linear_indexes = np.ravel_multi_index([np.arange(0, len(x), 1), np.arange(0, len(y), 1), coincidence_indexes],
                                          d_c_scan.shape)
    squeezed_scan = np.matrix.flatten(d_c_scan)
    kernel = np.reshape(np.cos(theta_a_arr) / r, (len(x), len(y))) * squeezed_scan[linear_indexes]
    migrated_point = np.abs(np.trapz(kernel, x, axis=0))
    migrated_point = np.abs(np.trapz(migrated_point, y, axis=0))
    return migrated_point


def kirchhoff_migration_2d(b_scan, h_ant, er, t0, tf, dt, x0, xf, qx, z0, zf):
    """Algorithm for Kirchhoff 2D migration
    Args:
      conn (Pipe): Connection pipe with the calling function.
      b_scan (nested-list float): Amplitudes of the B-Scan (should be pre-processed first).
      h_ant (float): Height of the antennas from ground [m].
      er (float): Ground apparent relative permittivity.
      t0 (float): Initial time value [s].
      tf (float): Final time value [s].
      dt (float): Time step [s].
      x0 (float): Initial horizontal axis value [m].
      xf (float): Final horizontal axis value [m].
      qx (float): Amount of values over the horizontal axis.
      z0 (float): Initial z-axis value [m].
      zf (float): Final z-axis value [m].
    """
    # Speed of light constant definition and calculation of propagation velocity in ground
    c0 = 3e8  # [m/s]
    vp = c0 / np.sqrt(er)  # [m/s]
    # Creation of time and space arrays
    x = np.linspace(x0, xf, qx)
    t = np.arange(t0, tf, dt)
    if len(t) != len(b_scan[0]):
        if len(t) > len(b_scan[0]):
            t = np.arange(t0, tf - dt, dt)
        else:
            t = np.arange(t0, tf + dt, dt)
    z = np.arange(z0, zf, dt * vp)
    # Calculate frequency domain array
    fs = 1 / dt
    f = np.linspace(-fs / 2, fs / 2, len(t))
    # Calculate half-derivative term and its multiplication with the B-Scan
    b_scan_f = np.fft.fftshift(np.fft.fft(b_scan, axis=0), axes=0)  # B-Scan in the frequency domain
    half_der = np.tile(np.sqrt(1j * 2 * np.pi * f.T), (qx, 1))  # Half derivative term
    d_b_scan = np.real(np.fft.ifft(np.fft.ifftshift(half_der * b_scan_f, axes=0), axis=0))  # Time domain expression
    # Create empty array for angles and integration kernel
    theta_a_arr = np.zeros((len(x), 1))
    theta_g_arr = np.zeros((len(x), 1))
    # Create empty matrix for the integral kernel
    kernel = np.zeros((qx, qx, len(z)))
    for i in range(0, qx):
        xp = x[i]
        for j in range(0, len(z)):
            zp = z[j]
            for k in range(0, qx):
                # Calls the transmission angle function to find both the ground and air transmission angles
                theta_a, theta_g = transmission_angles_2d(er, h_ant, xp, zp, x[k])
                theta_a_arr[k] = theta_a
                theta_g_arr[k] = theta_g
                # Calculate kernel values
            r = h_ant * (1 / np.cos(theta_a_arr)) + zp * (1 / np.cos(theta_g_arr))
            t_e = 2 * (h_ant * (1 / np.cos(theta_a_arr)) / c0 + zp * (1 / np.cos(theta_g_arr)) / vp)
            # Trace out hyperbola
            time_diff = np.tile(t, (qx, 1)) - np.tile(t_e, (1, len(t)))
            coincidence_indexes = np.argmin(np.abs(time_diff), axis=1)
            linear_indexes = np.ravel_multi_index([np.arange(0, len(x), 1), coincidence_indexes], d_b_scan.shape)
            squeezed_scan = np.matrix.flatten(d_b_scan)
            kernel[:, i, j] = np.reshape(np.cos(theta_a_arr) / np.sqrt(vp*r), (len(x),)) * squeezed_scan[linear_indexes]
    # Calculates the intrgral over the migration direction
    migrated_image = np.abs(np.trapz(kernel, x, axis=0))
    # Connects the pipe to the calculated migrated image
    return migrated_image


def kirchhoff_migration_3d_parallel(c_scan_scalars, h_ant, er, t0, tf, dt, x0, xf, qx, y0, yf, qy, z0, zf):
    """Algorithm for Kirchhoff 3D migration. Calls parallel 2D migrations.
    Args:
      c_scan_scalars (nested-list float): Amplitudes of the C-Scan (should be pre-processed first).
      h_ant (float): Height of the antennas from ground [m].
      er (float): Ground apparent relative permittivity.
      t0 (float): Initial time value [s].
      tf (float): Final time value [s].
      dt (float): Time step [s].
      x0 (float): Initial x-axis value [m].
      xf (float): Final x-axis value [m].
      qx (float): Amount of values over the x-axis.
      y0 (float): Initial y-axis value [m].
      yf (float): Final y-axis value [m].
      qy (float): Amount of values over the y-axis.
      z0 (float): Initial z-axis value [m].
      zf (float): Final z-axis value [m].
    """
    # Speed of light constant definition and calculation of propagation velocity in ground
    c0 = 3e8  # [m/s]
    vp = c0 / np.sqrt(er)  # [m/s]
    # Creation of time and space arrays
    z = np.arange(z0, zf, dt * vp)
    # Creates empty array for the migrated images
    migrated_image_one = np.zeros([qx, qy, len(z)])
    migrated_image_two = np.zeros([qx, qy, len(z)])
    # == Timer start ==
    tic = time.perf_counter()
    #migrated_image_full = kirchhoff_migration_3d(c_scan_scalars, h_ant, er, t0, tf, dt, x0, xf, qx, y0, yf, qy, z0, zf)
    # =================
    # Creates empty lists for the processes and the pipes to be appended to (first migration direction)
    pool = mp.Pool(processes=os.cpu_count())
    processes = []
    # Loops over all the positions of the x-axis
    for i in range(0, qx):
        print(f"Migrating over x-axis {i} of {qx-1}")
        # Calls the migration function with the corresponding migration pipe and the corresponding plane of the C-Scan
        result = pool.apply_async(kirchhoff_migration_2d,
                       args=(c_scan_scalars[i, :, :], h_ant, er, t0, tf, dt, y0, yf, qy, z0, zf))
    #     # Saves the process appending it to the processes list
        processes.append(result)
    for i in range(0, qx):
        # Recovers the values in the communication pipes
        migrated_image_one[i, :, :] = processes[i].get()
        print(f"Finished migration over x-axis {i} of {qx-1}")
    #     # Joins the processes to the main execution
    #     #processes[i].join()
    # # Creates empty lists for the processes and the pipes to be appended to (second migration direction)
    processes = []
    # # Loops over all the positions of the y-axis
    for j in range(0, qy):
        print(f"Migrating over y-axis {j} of {qy-1}")
        # Creates the communication pipes
        # Calls the migration function with the corresponding migration pipe and the corresponding plane of the C-Scan
        result = pool.apply_async(kirchhoff_migration_2d,
                       args=(c_scan_scalars[:, j, :], h_ant, er, t0, tf, dt, x0, xf, qx, z0, zf))
    #     # Starts the process for migration
    #     # p.start()
        # Joins the processes to the main execution
        processes.append(result)
    for j in range(0, qy):
        # Recovers the values in the communication pipes
        migrated_image_two[:, j, :] = processes[j].get()
        print(f"Finished migration over y-axis {j} of {qy-1}")
    #     # Joins the processes to the main execution
    # # Multiples the two migrated images to create the 3D migration
    migrated_image_full = np.multiply(migrated_image_one, migrated_image_two)
    # == Timer stop ===
    toc = time.perf_counter()
    print('Migration time:', toc - tic)
    # =================
    # Returns the migrated image and the length of the z-axis
    return migrated_image_full, len(z)

def kirchhoff_migration_3d_new_parallel(c_scan_scalars, h_ant, er, t0, tf, dt, x0, xf, qx, y0, yf, qy, z0, zf):
    c0 = 3e8  # [m/s]
    vp = c0 / np.sqrt(er)  # [m/s]
    # Creation of time and space arrays
    z = np.arange(z0, zf, dt * vp)
    tic = time.perf_counter()
    migrated_image_full = kirchhoff_migration_3d(c_scan_scalars, h_ant, er, t0, tf, dt, x0, xf, qx, y0, yf, qy, z0, zf)
    toc = time.perf_counter()
    print('Migration time:', toc - tic)
    # =================
    # Returns the migrated image and the length of the z-axis
    return migrated_image_full, len(z)

def store_migration_file(folder, title, migrated_image, h_ant, er, x0, xf, qx, y0, yf, qy, z0, zf, qz):
    """Stored the result of the 3D migrated image
    Args:
      folder (string): Folder/directory where to store the migrated image
      title (string): Title for the migrated image file
      migrated image (nested-list float): Migrated image amplitudes.
      h_ant (float): Height of the antennas from ground [m].
      er (float): Ground apparent relative permittivity.
      x0 (float): Initial x-axis value [m].
      xf (float): Final x-axis value [m].
      qx (float): Amount of values over the x-axis.
      y0 (float): Initial y-axis value [m].
      yf (float): Final y-axis value [m].
      qy (float): Amount of values over the y-axis.
      z0 (float): Initial z-axis value [m].
      zf (float): Final z-axis value [m].
      qz (float): Amount of values over the z-axis.
    """
    # Formats the output file name and creates the file
    output_file_name = folder + '/' + title + '.h5'
    output_file = h5py.File(output_file_name, 'w')
    # Creates and populates attributes of the Micreated Image file
    output_file.attrs['Title'] = title  # Title of the output file
    output_file.attrs['Relative permittivity'] = er  # Relative permittivity used for migration
    # Creates a group in the .h5 file to store the position of the measurement
    pos_grp = output_file.create_group('/Position')
    # Coordinates are stored in meters at the output file under the '/Position' group
    pos_grp.attrs['x0'] = x0
    pos_grp.attrs['y0'] = y0
    pos_grp.attrs['z0'] = z0
    pos_grp.attrs['xf'] = xf
    pos_grp.attrs['yf'] = yf
    pos_grp.attrs['zf'] = zf
    pos_grp.attrs['qx'] = qx
    pos_grp.attrs['qy'] = qy
    pos_grp.attrs['qz'] = qz
    # Height of the antena values are stored in data-set under '/Position' group
    pos_grp.attrs['h_ant_mig'] = h_ant
    # pos_grp.create_dataset('h', (qx, qy), dtype='f4', data=h_ant, compression="gzip")
    # A group to store the migrated image '/MigratedImage'
    mig_grp = output_file.create_group('/MigratedImage')
    # Migrated image values are stored in data-set under the '/MigratedImage' group
    mig_grp.create_dataset('Image', (qx, qy, qz), dtype='f4', data=migrated_image, compression="gzip")
    # Output file is closed with all the information written in it
    output_file.close()


def execute_migration(c_scan_file, title, er, pol, z0, zf, mode):
    """Stored the result of the 3D migrated image
    Args:
      c_scan_file (string): File with the C-Scan to be migrated.
      title (string): Title for the migrated image file.
      pol (string): Polarization of antennas ('x' or 'y').
      er (float): Ground apparent relative permittivity.
      z0 (float): Initial z-axis value [m].
      zf (float): Final z-axis value [m].
    """
    # Reads the folder of the file, this folder will be used to store the migrated image
    folder = os.path.dirname(c_scan_file)
    # Merged file is opened into data_frame variable
    data_frame = h5py.File(c_scan_file, 'r')
    # Time-domain lower and upper limits are retrieved
    t0 = data_frame['Time'].attrs['t0']
    tf = data_frame['Time'].attrs['tf']
    dt = data_frame['Time'].attrs['dt']
    qt = int(round(data_frame['Time'].attrs['q']))
    # x- and y-axis lower limits, upper limits and step are retrieved
    x0 = data_frame['Position'].attrs['x0']
    dx = data_frame['Position'].attrs['dx']
    xf = data_frame['Position'].attrs['xf']
    y0 = data_frame['Position'].attrs['y0']
    dy = data_frame['Position'].attrs['dy']
    yf = data_frame['Position'].attrs['yf']

    h_attr_flag = True
    if 'h' in data_frame['Position'].attrs.keys():
        ha = data_frame['Position'].attrs['h']
        # Verifies whether the antenna height from ground is a single value or if it is an array. If it is 
        # a single value, it is stored into an array making it as if it was given as an array.
        if isinstance(ha, (list, tuple, np.ndarray)):
            ha = np.mean(ha)
        h_attr_flag = True
    else:
        h_attr_flag = False
    print(f"Antenna height: {ha} m")
    # Amount of steps over each axis is calculated. Operation rounds up the division result as needed
    qx = int(round((xf - x0) / dx + 1))
    qy = int(round((yf - y0) / dy + 1))
    # Initializes C-Scan matrix
    c_scan_scalars = np.zeros([qx, qy, qt])
    if pol.lower() == "x":
        if not h_attr_flag:
            ha = data_frame['Position/h x-pol']
            ha = np.mean(ha)

        for count in range(0, qx):
            # Indexes used to retrieve individual planes of the C-Scan are calculated
            index_0 = count * qy
            index_f = (count + 1) * qy
            # C-Scan data is retrieved from the merged file
            c_scan_scalars[count, :, :] = data_frame['A-Scan/Re{A-Scan x-pol}'][index_0:index_f][:]
    else:
        if not h_attr_flag:
            ha = data_frame['Position/h y-pol']
            ha = np.mean(ha)

        for count in range(0, qx):
            # Indexes used to retrieve individual planes of the C-Scan are calculated
            index_0 = count * qy
            index_f = (count + 1) * qy
            # C-Scan data is retrieved from the merged file
            c_scan_scalars[count, :, :] = data_frame['A-Scan/Re{A-Scan y-pol}'][index_0:index_f][:]
    # Closes the .h5 file
    data_frame.close()
    # Calls the migration function and stores the obtained migrated image
    if mode == "2d":
        mi, qz = kirchhoff_migration_3d_parallel(c_scan_scalars, ha, er, t0, tf, dt, x0, xf, qx, y0, yf, qy, z0, zf)
    else:
        mi, qz = kirchhoff_migration_3d_new_parallel(c_scan_scalars, ha, er, t0, tf, dt, x0, xf, qx, y0, yf, qy, z0, zf)
    # Stores the obtained migrated image
    store_migration_file(folder, title, mi, ha, er, x0, xf, qx, y0, yf, qy, z0, zf, qz)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kirchhoff Migration')
    parser.add_argument('filepath', type=str, help='filepath of h5 file')
    parser.add_argument('output', type=str, help="title of migration")
    parser.add_argument('--er', default=2.58, type=float, help="relative permittivity of the ground")
    parser.add_argument('--polarization', default='x', type=str, choices=['x', 'y'], help="polarization")
    parser.add_argument('--z_ini', default=0.00, type=float, help="start height")
    parser.add_argument('--z_end', default=0.60, type=float, help="end height")
    parser.add_argument('--mode', default='2d', type=str, choices=['2d', '3d'], help="mode")

    args = parser.parse_args()

    file = args.filepath
    title = args.output
    pol = args.polarization
    er = args.er
    z_ini = args.z_ini
    z_end = args.z_end
    mode = args.mode
    print(f"Starting migration e_r: {er}, pol: {pol}, z_ini: {z_ini}, z_end: {z_end}, mode: {mode}")

    execute_migration(file, title, er, pol, z_ini, z_end, mode)
