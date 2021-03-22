import numpy as np
from lddecode.utils import unwrap_hilbert
from samplerate import resample
from vhsdecode.utils import \
    FiltersClass, firdes_lowpass, firdes_bandpass, \
    gen_wave_at_frequency, filter_plot, moving_average, \
    pad_or_truncate, auto_chop, zero_cross_det, plot_scope, dualplot_scope, plot_image


class HeadSwitchDetect:

    def __init__(self, fdc, fv=60, fs=40e6, blocklen=pow(2, 15)):
        self.harmonic_limit = 3
        self.samp_rate = fs
        self.fdc = fdc
        self.fv = fv
        self.blocklen = blocklen
        self.audio_rate = 192000
        self.filename = "headswitch_log.wav"
        self.tempfile = open(self.filename + '.part.raw', 'wb')
        self.avg_max_vel = list()
        self.avg_max_acc = list()

        iir_slow = firdes_lowpass(self.samp_rate, self.harmonic_limit * self.fv, self.harmonic_limit * self.fv)
        self.slow_filter = FiltersClass(iir_slow[0], iir_slow[1], self.samp_rate)

        iir_bandpass = firdes_bandpass(
            self.samp_rate,
            fdc * 0.1,
            100e3,
            fdc * 1.1,
            100e3
        )

        self.bandpass = FiltersClass(iir_bandpass[0], iir_bandpass[1], self.samp_rate)


    def hhtdeFM(self, data):
        instf, t = inst_freq(data)
        return np.add(np.multiply(instf, -self.samp_rate), self.samp_rate /2)

    def htdeFM(self, data):
        return unwrap_hilbert(data, self.samp_rate)

    def deFM(self, data):
        return self.htdeFM(data)

    # Measures the head switch jitter
    def head_switch_jitter(self, data):
        narrowband = self.bandpass.lfilt(data.real)

        freq = self.deFM(narrowband)
        centered = np.add(freq, -self.offset)
        # plot_scope(centered[:1024])

        velocity = self.slow_filter.lfilt(centered)
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
               np.append(acceleration, acceleration[len(acceleration) - 1]), \
               average_vel_offset

    # Measures the head switch jitter
    #def head_switch_jitter(self, data):
    #    narrowband = self.bandpass.lfilt(data.real)
    #    freq = unwrap_hilbert(narrowband, self.samp_rate) - self.fdc
    #    velocity = self.slow_filter.lfilt(freq)
    #    acceleration = np.diff(velocity)
    #    rel_velocity = np.cumsum(acceleration)
    #    return velocity, \
    #           np.append(acceleration, acceleration[len(acceleration) - 1]),

    def to_wave(self, ch0, ch1):
        ratio = self.audio_rate / self.samp_rate
        left = resample(np.multiply(ch0, 0x7FFF), ratio, converter_type='linear')
        right = resample(np.multiply(ch1, 0x7FFF), ratio, converter_type='linear')
        interleaved = np.zeros(len(left)+len(right))
        interleaved[::2] = left
        interleaved[1::2] = right
        return np.asarray(interleaved, dtype=np.int16)

    def publish(self, wave):
        return

    # writes a temporary raw file
    def work(self, data):
        vel, acc = self.head_switch_jitter(data)
        self.avg_max_vel.append(np.max(vel))
        self.avg_max_acc.append(np.max(acc))
        scale_vel = 40 # moving_average(self.avg_max_vel)
        scale_acc = 1 # moving_average(self.avg_max_acc)
        wave = self.to_wave(np.multiply(vel, 1/scale_vel), np.multiply(acc, 1/scale_acc))
        self.tempfile.write(wave)
