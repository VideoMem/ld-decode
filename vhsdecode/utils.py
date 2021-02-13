import numpy as np
import scipy.signal as signal
from lddecode.utils import pi, tau


def gen_wave_at_frequency(frequency, sample_frequency, num_samples, gen_func=np.sin):
    """Generate a sine wave with the specified parameters."""
    samples = np.arange(num_samples)
    wave_scale = frequency / sample_frequency
    return gen_func(2 * np.pi * wave_scale * samples)


def moving_average(data_list, window=1024):
    average = sum(data_list) / len(data_list)

    if len(data_list) >= window:
        data_list.pop()

    return average


def design_lowpass(samp_rate, cutoff, transition_width, order_limit=6):
    passband, stopband = cutoff, cutoff + transition_width
    max_loss_passband = 3  # The maximum loss allowed in the passband
    min_loss_stopband = 30  # The minimum loss allowed in the stopband
    order, normal_cutoff = signal.buttord(passband, stopband, max_loss_passband,
                                          min_loss_stopband, samp_rate)
    if order > order_limit:
        print('WARN: Limiting order of the filter from %d to %d' % (order, order_limit))
        order = order_limit
    return passband, stopband, order, normal_cutoff


def firdes_lowpass(samp_rate, cutoff, transition_width, order_limit=6):
    passband, stopband, order, normal_cutoff =\
        design_lowpass(samp_rate, cutoff, transition_width, order_limit)
    return signal.butter(order, normal_cutoff, btype="lowpass", fs=samp_rate)


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


class FilterWithState:
    def __init__(self, iir_b, iir_a, samp_rate):
        self.iir_b, self.iir_a = iir_b, iir_a
        self.z = signal.lfilter_zi(self.iir_b, self.iir_a)
        self.samp_rate = samp_rate

    def rate(self):
        return self.samp_rate

    def work(self, data):
        output, self.z = signal.lfilter(self.iir_b, self.iir_a, data, zi=self.z)
        return output

