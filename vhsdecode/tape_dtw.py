"""
    It provides a set of functions to DTW (Dynamic Time Warping) the tape signal
    in order to remove the reading jitter caused by mechanical issues.
    It also detects the head switch point in the process.
"""

import numpy as np
from pyhht.utils import inst_freq
from vhsdecode.utils import FiltersClass, firdes_lowpass, firdes_bandpass, gen_wave_at_frequency, filter_plot


class TimeWarper:
    # fdc chroma subcarrier frequency
    def __init__(self, fdc, fv=60, fs=40e6, blocklen=pow(2, 15)):
        self.samp_rate = fs
        self.fdc = fdc
        self.fdc_wave = gen_wave_at_frequency(fdc, fs, blocklen)
        iir_slow = firdes_lowpass(self.samp_rate, 180, 1e3)
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

    # Measures the head switch jitter
    def head_switch_jitter(self, data):
        narrowband = self.bandpass.work(data.real)
        inst, t = inst_freq(narrowband)
        freq = np.multiply(inst, self.samp_rate)
        centered = np.add(freq, -self.offset)
        filtered = self.slow_filter.workl(centered)
        #print('Go print go!', np.mean(filtered), self.offset, np.max(filtered))
        return filtered


