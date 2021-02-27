"""
    It provides a set of functions to DTW (Dynamic Time Warping) the tape signal
    in order to remove the reading jitter caused by mechanical issues.
    It also detects the head switch point in the process.
"""

import numpy as np
from scipy.signal import chirp
from pyhht.utils import inst_freq
from vhsdecode.utils import \
    FiltersClass, firdes_lowpass, firdes_bandpass, \
    gen_wave_at_frequency, filter_plot, moving_average, \
    pad_or_truncate, auto_chop, plot_scope
from lddecode.utils import unwrap_hilbert

from samplerate import resample
from math import pi

class TimeWarper:
    # fdc chroma subcarrier frequency
    def __init__(self, fdc, fv=60, fs=40e6, blocklen=pow(2, 15)):
        self.dx = 128
        self.harmonic_limit = 3
        self.samp_rate = fs
        self.fdc = fdc
        self.fv = fv
        self.blocklen = blocklen
        self.fdc_lut, first, last = auto_chop(gen_wave_at_frequency(fdc - 10e3, fs, blocklen))
        self.fdc_wave = gen_wave_at_frequency(fdc, fs, blocklen)
        self.roll = blocklen - last

        #instf, t = inst_freq(self.fdc_wave)
        #self.offset = np.mean(np.multiply(instf, self.samp_rate))
        #instf = unwrap_hilbert(self.fdc_wave, fs)

        iir_slow = firdes_lowpass(self.samp_rate, self.harmonic_limit * self.fv, 1e3)
        iir_demod = firdes_lowpass(self.samp_rate, self.fdc / 20, self.fdc / 10)
        self.slow_filter = FiltersClass(iir_slow[0], iir_slow[1], self.samp_rate)
        self.demod_filter = FiltersClass(iir_demod[0], iir_demod[1], self.samp_rate)

        iir_bandpass = firdes_bandpass(
            self.samp_rate,
            fdc * 0.9,
            100e3,
            fdc * 1.1,
            100e3
        )

        #filter_plot(iir_bandpass[0], iir_bandpass[1], self.samp_rate, 'bandpass', 'Dchroma notch')
        self.bandpass = FiltersClass(iir_bandpass[0], iir_bandpass[1], self.samp_rate)
        self.last_velocity_offset = list()
        self.average_offset = list()

        #self.offset = 0
        #vel, _, offset = self.head_switch_jitter(self.fdc_wave)
        #self.last_velocity_offset.clear()
        #self.offset = offset
        self.offset = np.mean(self.deFM(self.fdc_wave))

        self.sweep_test()
        #test_wave = gen_wave_at_frequency(fdc + 10e3, fs, blocklen)

        #centered, _, offset = self.head_switch_jitter(test_wave)
        #assert offset == 10e3, "Offset not zero!, got %.2f" % offset
        #self.last_velocity_offset.clear()
        #print('computed offset', offset)
        #self.offset -= offset
        #centered, _, offset = self.head_switch_jitter(self.fdc_wave)
        #self.last_velocity_offset.clear()
        #print('computed offset', offset)
        self.clear()
        #exit(0)

    def clear(self):
        self.average_offset.clear()
        self.last_velocity_offset.clear()

    def carrier(self):
        self.fdc_lut = np.roll(self.fdc_lut, self.roll)
        padded = np.append(self.fdc_lut, self.fdc_lut[:self.blocklen - len(self.fdc_lut)])
        assert len(padded) == self.blocklen, 'error at carrier generation'
        return padded

    def heterodyne(self, data):
        xlated = np.multiply(data, self.carrier())
        return self.demod_filter.workl(xlated)

    def hhtdeFM(self, data):
        instf, t = inst_freq(data)
        return np.add(np.multiply(instf, -self.samp_rate), self.samp_rate /2)

    def htdeFM(self, data):
        return unwrap_hilbert(data, self.samp_rate)

    def deFM(self, data):
        return self.hhtdeFM(data)

    def sweep_test(self):
        df = np.linspace(-10e3, 10e3, num=512)
        table = list()
        min_table = list()
        for deviation in df:
            test_wave = gen_wave_at_frequency(self.fdc + deviation, self.samp_rate, self.blocklen)
            defm = self.deFM(test_wave)
            table.append(np.mean(defm))
            min_table.append(np.min(defm))
        #plot_scope(table)
        #self.chirp_test()
        #exit(0)

    def chirp_test(self):
        t = np.linspace(0, 10e3, self.blocklen)
        w = chirp(t, f0=self.fdc, f1=self.fdc+10e3, t1=self.blocklen, method='linear')
        #plot_scope(w[:1024])
        #plot_scope(w[len(w) - 1024:])
        table = self.deFM(w)
        #plot_scope(table)

    # Measures the head switch jitter
    def head_switch_jitter(self, data):

        narrowband = self.bandpass.work(data.real)

        freq = self.deFM(narrowband)
        centered = np.add(freq, -self.offset)
        #plot_scope(centered[:1024])

        velocity = self.slow_filter.workl(centered)
        velocity_offset = np.mean(velocity)
        self.last_velocity_offset.append(velocity_offset)
        average_vel_offset = moving_average(self.last_velocity_offset, window=10)
        rel_velocity = np.add(
            velocity,
            -average_vel_offset
        )

        acceleration = np.diff(velocity)

        print('Average offset %.2f, max %.2f, min %.2f ' % (average_vel_offset, np.max(velocity), np.min(velocity)))
        return velocity, \
            np.append(acceleration, acceleration[len(acceleration)-1]), \
            average_vel_offset


    def get_control(self, velocity, converter='linear'):
        assert self.blocklen % self.dx == 0, 'dx should be a divisor of blocklen'
        ratio = 1 / self.dx
        control = resample(velocity, ratio=ratio, converter_type=converter)
        assert len(control) == int(len(velocity) / self.dx), \
            'expected %d, got %d' % (len(control), int(len(velocity) / self.dx))
        return control

    def block_resample(self, data, control, converter='linear'):
        data_chunks = np.split(data, self.dx)
        control_id = 0
        #print(self.fdc)
        resampled = np.asarray([])
        #plot_scope(control)
        for chunk in data_chunks:
            #if control[control_id] > 0:
            #    adjust = self.fdc - control[control_id])
            ratio = self.fdc - control[control_id] / self.fdc
            ratio = np.clip(ratio, a_max=256, a_min=1/256).astype(np.float64)
            bres = resample(chunk, ratio=ratio, converter_type=converter)
            resampled = np.append(resampled, bres)
            #print('Adjusting velocity point %d (df %.2f) by %.2f%%' % (control_id, control[control_id], adjust * 100))
            control_id += 1

        #resampled = pad_or_truncate(resampled, data)
        #diff = len(data) - len(resampled)
        #if diff > 0:
        #    resampled = np.insert(resampled, 0, np.zeros(abs(diff)))
        #else:
        #    resampled = resampled[:len(data)]

        #assert len(resampled) == len(data), \
        #    'Unexpected resample result, waiting %d got %d' % (len(data), len(resampled))

        return resampled

    def velocity_compensator(self, data):
        velocity, acceleration, average_velocity =\
            self.head_switch_jitter(data)
        control = self.get_control(np.add(velocity, average_velocity))
        resampled = self.block_resample(data, control)
        resampled = pad_or_truncate(resampled, data)
        return pad_or_truncate(resampled, data)
