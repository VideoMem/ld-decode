import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt


def gen_wave_at_frequency(frequency, sample_frequency, num_samples, gen_func=np.sin):
    """Generate a sine wave with the specified parameters."""
    samples = np.arange(num_samples)
    wave_scale = frequency / sample_frequency
    return gen_func(2 * np.pi * wave_scale * samples)


def gen_compl_wave_at_frequency(frequency, sample_frequency, num_samples):
    """Generate a sine wave with the specified parameters."""
    samples = np.arange(num_samples)
    wave_scale = frequency / sample_frequency
    return np.exp(-2 * np.pi * wave_scale * samples * 1j)


# returns the indexes where the signal crosses zero
def zero_cross_det(data):
    return np.where(np.diff(np.sign(data)))[0]


# crops a wave at the zero cross detection
def auto_chop(data):
    zeroes = zero_cross_det(data)
    first = zeroes[0]
    last = zeroes[len(zeroes) - 1]
    sign_first = data[first + 1]
    sign_last = data[last + 1]

    if sign_first > 0 and sign_last > 0:
        last = last
    else:
        last = zeroes[len(zeroes) - 2]

    return data[first:last], first, last


# simple scope plot
def plot_scope(data):
    fig, ax1 = plt.subplots()
    ax1.plot(data, color="#FF0000")
    plt.show()


# simple scope plot
def dualplot_scope(ch0, ch1):
    fig, ax1 = plt.subplots()
    ax1.plot(ch0, color="#FF0000")
    ax1.plot(ch1, color="#0000FF")
    plt.show()


# pads data with filler is len(data) < len(filler), otherwise truncates it
def pad_or_truncate(data, filler):
    if len(filler) > len(data):
        err = len(filler) - len(data)
        data = np.append(data, filler[len(data) - err: len(data)])
    else:
        data = data[len(data) - len(filler):]

    return data


def moving_average(data_list, window=1024):
    #average = np.mean(data_list)
    average = sum(data_list) / len(data_list)

    if len(data_list) >= window:
        data_list.pop()

    return average


def design_filter(samp_rate, passband, stopband, order_limit=20):
    max_loss_passband = 3  # The maximum loss allowed in the passband
    min_loss_stopband = 30  # The minimum loss allowed in the stopband
    order, normal_cutoff = signal.buttord(passband, stopband, max_loss_passband,
                                          min_loss_stopband, samp_rate)
    if order > order_limit:
        print('WARN: Limiting order of the filter from %d to %d' % (order, order_limit))
        order = order_limit
    return order, normal_cutoff


def firdes_lowpass(samp_rate, cutoff, transition_width, order_limit=20):
    passband, stopband = cutoff, cutoff + transition_width
    order, normal_cutoff =\
        design_filter(samp_rate, passband, stopband, order_limit)
    return signal.butter(order, normal_cutoff, btype="lowpass", fs=samp_rate)


def firdes_highpass(samp_rate, cutoff, transition_width, order_limit=20):
    passband, stopband = cutoff, cutoff + transition_width
    order, normal_cutoff =\
        design_filter(samp_rate, passband, stopband, order_limit)
    return signal.butter(order, normal_cutoff, btype="highpass", fs=samp_rate)


def firdes_bandpass(samp_rate, f0, t0, f1, t1, order_limit=20):
    assert f0 < f1, 'First frequency specified is higher than the second one, swap them'
    passband, stopband = (f1, f1 + t1), (f0, f0 - t0)
    order, normal_cutoff =\
        design_filter(samp_rate, passband, stopband, order_limit)
    return signal.butter(order, normal_cutoff, btype="bandpass", fs=samp_rate)


# makes a bode plot of an IIR filter
def filter_plot(iir_b, iir_a, samp_rate, type, title):
    import matplotlib.pyplot as plt
    from math import log10

    nyq = samp_rate / 2
    w, h = signal.freqz(iir_b, iir_a, worN=np.logspace(0, log10(nyq), 10000), fs=samp_rate)
    fig = plt.figure()
    plt.semilogx(w, 20 * np.log10(abs(h)))
    ax1 = fig.add_subplot()
    plt.ylim([-42, 3])
    plt.title('Butterworth IIR %s fit to\n%s' % (type, title))
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Amplitude [dB]')
    plt.grid(which='both', axis='both')
    ax2 = ax1.twinx()
    angles = np.unwrap(np.angle(h))
    plt.plot(w, angles, 'g')
    plt.ylabel('Angle [degrees]', color='g')
    plt.show()


class FiltersClass:
    def __init__(self, iir_b, iir_a, samp_rate):
        self.iir_b, self.iir_a = iir_b, iir_a
        self.z = signal.lfilter_zi(self.iir_b, self.iir_a)
        self.samp_rate = samp_rate

    def rate(self):
        return self.samp_rate

    def filtfilt(self, data):
        output = signal.filtfilt(self.iir_b, self.iir_a, data)
        return output

    def lfilt(self, data):
        output, self.z = signal.lfilter(self.iir_b, self.iir_a, data, zi=self.z)
        return output

