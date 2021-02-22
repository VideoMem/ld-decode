"""
    It provides a set of functions to DTW (Dynamic Time Warping) the tape signal
    in order to remove the reading jitter caused by mechanical issues.
    It also detects the head switch point in the process.
"""

import numpy as np
from pyhht.utils import inst_freq
from vhsdecode.utils import \
    FiltersClass, firdes_lowpass, firdes_bandpass, \
    gen_wave_at_frequency, filter_plot, moving_average


class TimeWarper:
    # fdc chroma subcarrier frequency
    def __init__(self, fdc, fv=60, fs=40e6, blocklen=pow(2, 15)):
        self.samp_rate = fs
        self.fdc = fdc
        self.fv = fv
        self.blocklen = blocklen
        self.fdc_wave = gen_wave_at_frequency(fdc, fs, blocklen)
        iir_slow = firdes_lowpass(self.samp_rate, 3 * self.fv, 1e3)
        self.slow_filter = FiltersClass(iir_slow[0], iir_slow[1], self.samp_rate)
        instf, t = inst_freq(self.fdc_wave)
        self.offset = np.multiply(np.mean(instf), self.samp_rate)
        iir_bandpass = firdes_bandpass(
            self.samp_rate,
            fdc * 0.9,
            100e3,
            fdc * 1.1,
            100e3
        )
        #filter_plot(iir_bandpass[0], iir_bandpass[1], self.samp_rate, 'bandpass', 'chroma notch')
        self.bandpass = FiltersClass(iir_bandpass[0], iir_bandpass[1], self.samp_rate)
        self.last_velocity_offset = list()

    # Measures the head switch jitter
    def head_switch_jitter(self, data):

        narrowband = self.bandpass.work(data.real)
        inst, t = inst_freq(narrowband)
        freq = np.multiply(inst, -self.samp_rate)
        centered = np.add(freq, self.offset)

        velocity = self.slow_filter.workl(centered)
        velocity_offset = np.mean(velocity)
        self.last_velocity_offset.append(velocity_offset)
        average_vel_offset = moving_average(self.last_velocity_offset, window=10)
        rel_velocity = np.add(
            velocity,
            -average_vel_offset
        )

        acceleration = np.diff(velocity)

        print('Go print go!', average_vel_offset, np.max(velocity))
        return rel_velocity, \
            np.append(acceleration, acceleration[len(acceleration)-1]), \
            average_vel_offset


