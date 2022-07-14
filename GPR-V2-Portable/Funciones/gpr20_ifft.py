import numpy as np
import matplotlib.pyplot as plt

def inverse_fast_fourier(signal_freq, freq_dom):
    """Calculates the inverse fast Fourier transform of the given signal.
    Args:
      signal_freq (float array): signal to which the IFFT is calculated from.
      freq_dom (float array): array of the frequencies corresponding to the frequency-domain signal.
    Returns:
      signal_time (float array): time-domain signal obtained from the IFFT implementation.
      time_dom (float array): array of time corresponding to the time-domain signal.
      signal_freq (float array): frequency-domain signal with the processing done over it.
      freq_dom (float array): array of the frequencies corresponding to the frequency-domain signal with processing.
    """

    # Retrieve the frequency step from the frequency array
    df = freq_dom[1] - freq_dom[0]

    # Check whether the signal is one-sided or two-sided by checking the frequency domain vector first value
    # A bool variable is used for additional clarification that the signal is one- or two-sided
    st_freq = freq_dom[0]
    if st_freq >= 0:
        one_sided = True

        # If the signal is one sided a small time delay is added to it in order to have a more intuitive representation
        # of the pulses. This delay does not change the meaning of the measurement because the whole signal is affected
        # by it
        t_del = 5e-9
        delay = np.exp(-1j * 2 * np.pi * freq_dom * t_del)
        # Delay is applied to the sinal and a hamming window is applied to smooth the signal
        signal_freq = delay * signal_freq * np.hamming(len(freq_dom))
    else:
        one_sided = False

    # If the signal is one sided then is necessary to check whether to zero-pad the signal from f = 0 to the starting
    # frequency or if the starting frequency is f = 0
    if one_sided:
        if st_freq > 0:
            freq_dom = np.arange(0, freq_dom[-1], df)
            index_st = np.where(freq_dom >= st_freq)[0][0]
            signal_freq = np.append(np.zeros(index_st - 1), signal_freq)

    # IFFT is calculated:
    if one_sided:
        # If the signal is one-sided the positive side of the signal (known) is mirrored into the negative frequencies
        # as the complex conjugate
        positive_side = signal_freq
        negative_side = np.flip(np.conj(positive_side)[0:len(positive_side)], 0)
        signal_freq = np.append(negative_side, positive_side)

        # The frequency array is also mirrored
        freq_dom = np.append(-np.flip(freq_dom, 0), freq_dom)

        # The frequency domain signal is organized with np.fftshift(), the IFFT is calculated with np.ifft() and then is
        # organized using np.ifftshift()
        org_signal_freq = np.fft.fftshift(signal_freq)
        signal_time = np.fft.ifft(org_signal_freq)
        signal_time = np.fft.ifftshift(signal_time)
    else:
        # The frequency domain signal is organized with np.fftshift(), the IFFT is calculated with np.ifft() and then is
        # organized using np.ifftshift()
        org_signal_freq = np.fft.fftshift(signal_freq)
        signal_time = np.fft.ifft(org_signal_freq)
        signal_time = np.fft.ifftshift(signal_time)

    # Construction of the time domain array
    nf = len(freq_dom)
    fs = nf * df
    dt = 1 / fs
    time_dom = np.arange(- nf * dt / 2, (nf - 1) * dt / 2, dt)

    # # Amplitude correction of the time domain signal
    # signal_time = fs * signal_time

    return signal_time, time_dom, signal_freq, freq_dom

def cosine_with_shift(dom, a, xo):
    f = a * np.cos(2 * np.pi * xo * dom) * np.exp(- 2j * np.pi * xo * dom)

    return f

def cosine_with_shift_inverse(dom, a, xo):
    f = np.zeros(len(dom))

    index_one = np.where(dom >= 0)[0][0]
    index_two = np.where(dom >= xo + xo)[0][0]

    f[index_one] = a / 2
    f[index_two] = a / 2
    return f

if __name__ == '__main__':
    # The following runs an implementation example of the IFFT function
    # First the ideal representation of a time-domain and frequency-domain pair of functions is given. This ideal
    # representation is obtained through the inverse Fourier transform integral. Later the discrete frequency- domain
    # signal is built. The frequency-domain signal is fed to the IFFT algorithm, which gives back the time-domain
    # representation of the signal. All four signals are then plotted: frequency-domain ideal, time-domain ideal,
    # frequency-domain discrete and time-domain discrete.

    # Definition of the ideal frequency vector:
    st_freq_ideal = -12e9 # Starting frequency
    en_freq_ideal = 12e9  # Ending frequency
    Nf_ideal = 2 ** 15 # Number of points

    freq_ideal = np.linspace(st_freq_ideal, en_freq_ideal, Nf_ideal)
    df_ideal = freq_ideal[1] - freq_ideal[0]
    Fs_ideal = 2 * Nf_ideal * df_ideal

    freq_id_hf = np.arange(0, en_freq_ideal, df_ideal)

    # Definition of the ideal time vector:
    time_ideal = np.linspace(-4e-9, 4e-9, Nf_ideal)

    # Definition of the discrete frequency vector:
    st_freq_discrete = 1e9  # Starting frequency
    en_freq_discrete = 6e9  # Ending frequency
    Nf_discrete = 2 ** 15  # Number of points

    freq_discrete = np.linspace(st_freq_discrete, en_freq_discrete, Nf_discrete)
    df_discrete = freq_discrete[1] - freq_discrete[0]

    # ==================================================================================================================

    # Calls the function to create the ideal frequency signal
    ideal_signal_fd = cosine_with_shift(freq_ideal, 1, 1e-9)  # Param: vect. frecuencia - alitud - Corrimiento - Desviacion

    # Calls the function to create the ideal time signal
    ideal_signal_td = cosine_with_shift_inverse(time_ideal, 1, 1e-9)  # Param: vect. tiempo - alitud - Corrimiento - Desviacion

    # Calls the function to create the discrete frequency signal
    signal_fd = cosine_with_shift(freq_discrete, 1, 1e-9)  # Param: vect. frecuencia - alitud - Corrimiento - Desviacion

    # Calls the function to calculate the IFFT of the discrete signal
    signal_td, time_discrete, new_signal_fd, new_freq_discrete = inverse_fast_fourier(signal_fd, freq_discrete)

    # ==================================================================================================================

    # Plot all signals
    figure, ((axis1, _, axis7), (axis2, axis5, axis8), (axis3, axis6, axis9), (axis4, _, axis10)) = plt.subplots(4,3)
    figure.suptitle('Example of IFFT for VNA acquired signals')

    # Plot of ideal frequency-domain signal
    color_fig = 'tab:blue'
    axis1.set_ylabel('Magnitude', color=color_fig)
    axis1.plot(freq_ideal, np.abs(ideal_signal_fd), color='tab:blue')
    axis1.tick_params(axis='y', labelcolor=color_fig)
    axis1.set_xlim(st_freq_ideal, en_freq_ideal)
    axis1.set_xlabel('Frequency [Hz]')
    axis1.grid()
    axis1.set_title('Ideal frequency signal')

    color_fig = 'tab:red'
    axis2.set_ylabel('Phase [deg]', color=color_fig)
    axis2.plot(freq_ideal, np.degrees(np.angle(ideal_signal_fd)), color=color_fig)
    axis2.tick_params(axis='y', labelcolor=color_fig)
    axis2.set_xlim(st_freq_ideal, en_freq_ideal)
    axis2.set_xlabel('Frequency [Hz]')
    axis2.grid()

    # Plot of ideal time-domain signal
    color_fig = 'tab:blue'
    axis3.set_ylabel('Magnitude', color=color_fig)
    axis3.plot(time_ideal, np.abs(ideal_signal_td), color=color_fig)
    axis3.tick_params(axis='y', labelcolor=color_fig)
    axis3.set_xlim(time_ideal[0], time_ideal[-1])
    axis3.set_xlabel('Time [s]')
    axis3.grid()
    axis3.set_title('Ideal time signal')

    color_fig = 'tab:red'
    axis4.set_ylabel('Phase [deg]', color=color_fig)
    axis4.plot(time_ideal, np.degrees(np.angle(ideal_signal_td)), color=color_fig)
    axis4.tick_params(axis='y', labelcolor=color_fig)
    axis4.set_xlim(time_ideal[0], time_ideal[-1])
    axis4.set_xlabel('Time [s]')
    axis4.grid()

    # Plot of original frequency-domain discrete signal
    color_fig = 'tab:blue'
    axis5.set_ylabel('Magnitude', color=color_fig)
    axis5.plot(freq_discrete, np.abs(signal_fd), color=color_fig)
    axis5.tick_params(axis='y', labelcolor=color_fig)
    axis5.set_xlim(st_freq_ideal, en_freq_ideal)
    axis5.set_xlabel('Frequency [Hz]')
    axis5.grid()
    axis5.set_title('VNA captured signal')

    color_fig = 'tab:red'
    axis6.set_ylabel('Magnitude', color=color_fig)
    axis6.plot(freq_discrete, np.degrees(np.angle(signal_fd)), color=color_fig)
    axis6.tick_params(axis='y', labelcolor=color_fig)
    axis6.set_xlim(st_freq_ideal, en_freq_ideal)
    axis6.set_xlabel('Frequency [Hz]')
    axis6.grid()

    # Plot of mirrored/complex conjugate frequency-domain discrete signal
    color_fig = 'tab:blue'
    axis7.set_ylabel('Magnitude', color=color_fig)
    axis7.plot(new_freq_discrete, np.abs(new_signal_fd), color='tab:blue')
    axis7.tick_params(axis='y', labelcolor=color_fig)
    axis7.set_xlim(st_freq_ideal, en_freq_ideal)
    axis7.set_xlabel('Frequency [Hz]')
    axis7.grid()
    axis7.set_title('Mirrored frequency signal')

    color_fig = 'tab:red'
    axis8.set_ylabel('Phase [deg]', color=color_fig)
    axis8.plot(new_freq_discrete, np.degrees(np.angle(new_signal_fd)), color=color_fig)
    axis8.tick_params(axis='y', labelcolor=color_fig)
    axis8.set_xlim(st_freq_ideal, en_freq_ideal)
    axis8.set_xlabel('Frequency [Hz]')
    axis8.grid()

    # Plot of time-domain discrete signal calculated with IFFT
    color_fig = 'tab:blue'
    axis9.set_ylabel('Magnitude', color=color_fig)
    axis9.plot(time_discrete, np.abs(signal_td), color='tab:blue')
    axis9.tick_params(axis='y', labelcolor=color_fig)
    axis9.set_xlim(time_ideal[0], time_ideal[-1])
    axis9.set_xlabel('Time [s]')
    axis9.grid()
    axis9.set_title('IFFT time signal')

    color_fig = 'tab:red'
    axis10.set_ylabel('Phase [deg]', color=color_fig)
    axis10.plot(time_discrete, np.degrees(np.angle(signal_td)), color=color_fig)
    axis10.tick_params(axis='y', labelcolor=color_fig)
    axis10.set_xlim(time_ideal[0], time_ideal[-1])
    axis10.set_xlabel('Time [s]')
    axis10.grid()

    plt.grid(True, 'both', 'both')
    figure.tight_layout(h_pad=0.1)
    plt.show()