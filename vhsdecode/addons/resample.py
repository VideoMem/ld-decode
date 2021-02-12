from scipy import signal
from fractions import Fraction
from samplerate import resample

class ArbitraryResampler:

    def __init__(self, samp_rate):
        self.rate = samp_rate

    # returns an approximated rational of a float
    def rationalize(self, float_scale, limit=1000):
        fraction = Fraction(float_scale).limit_denominator(limit)
        return fraction.numerator, fraction.denominator

    def rational_resample(self, data, n, d):
        upsize = len(data) * n
        downsize = round(upsize / d)
        upscaled = signal.resample(data, upsize)
        return signal.resample(upscaled, downsize)

    # finds the best fraction to down resample
    def autorational(self, data, newrate):
        n, d = self.rationalize(newrate / self.rate)
        return self.rational_resample(data, n, d)

    def ratio(self, rate):
        return rate / self.rate

    def linear(self, data, rate):
        return resample(data, self.ratio(rate), converter_type='linear')

    def naive(self, data, rate):
        return resample(data, self.ratio(rate), converter_type='zero_order_hold')

    def sinc(self, data, rate):
        return resample(data, self.ratio(rate), converter_type='sinc_fastest')

    def best(self, data, rate):
        return resample(data, self.ratio(rate), converter_type='sinc_best')
