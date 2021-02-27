import math
import numpy as np
import scipy.signal as sps
import copy

import itertools

import lddecode.core as ldd
import lddecode.utils as lddu
import vhsdecode.utils as utils
import vhsdecode.tape_dtw as dtw
from lddecode.utils import unwrap_hilbert

import vhsdecode.formats as vhs_formats

import zmq
import vhsdecode.addons.zmq_grc as zm
from collections import deque
from fractions import Fraction
from samplerate import resample
from pyhht.utils import inst_freq
from pyhht import EmpiricalModeDecomposition as EMD

try:
    import pyfftw.interfaces.numpy_fft as npfft
    import pyfftw.interfaces

    pyfftw.interfaces.cache.enable()
    pyfftw.interfaces.cache.set_keepalive_time(10)
except ImportError:
    import numpy.fft as npfft


def toDB(val):
    return 20 * np.log10(val)


def fromDB(val):
    return 10.0 ** (val / 20.0)


def chroma_to_u16(chroma):
    """Scale the chroma output array to a 16-bit value for output."""
    S16_ABS_MAX = 32767

    if np.max(chroma) > S16_ABS_MAX or abs(np.min(chroma)) > S16_ABS_MAX:
        ldd.logger.warning("Chroma signal clipping.")

    return np.uint16(chroma + S16_ABS_MAX)


def acc(chroma, burst_abs_ref, burststart, burstend, linelength, lines):
    """Scale chroma according to the level of the color burst on each line."""

    output = np.zeros(chroma.size, dtype=np.double)
    for linenumber in range(16, lines):
        linestart = linelength * linenumber
        lineend = linestart + linelength
        line = chroma[linestart:lineend]
        output[linestart:lineend] = acc_line(line, burst_abs_ref, burststart, burstend)

    return output


def acc_line(chroma, burst_abs_ref, burststart, burstend):
    """Scale chroma according to the level of the color burst the line."""
    output = np.zeros(chroma.size, dtype=np.double)

    line = chroma
    burst_abs_mean = lddu.rms(line[burststart:burstend])
    # np.sqrt(np.mean(np.square(line[burststart:burstend])))
    #    burst_abs_mean = np.mean(np.abs(line[burststart:burstend]))
    scale = burst_abs_ref / burst_abs_mean if burst_abs_mean != 0 else 1
    output = line * scale

    return output


def gen_low_shelf(f0, dbgain, qfactor, fs):
    """Generate low shelving filter coeficcients (digital).
    f0: The frequency where the gain in decibel is at half the maximum value.
       Normalized to sampling frequency, i.e output will be filter from 0 to 2pi.
    dbgain: gain at the top of the shelf in decibels
    qfactor: determines shape of filter TODO: Document better
    fs: sampling frequency

    Based on: https://www.w3.org/2011/audio/audio-eq-cookbook.html
    """
    # Not sure if the implementation is quite correct here but it seems to work
    a = 10 ** (dbgain / 40.0)
    w0 = 2 * math.pi * (f0 / fs)
    alpha = math.sin(w0) / (2 * qfactor)

    cosw0 = math.cos(w0)
    asquared = math.sqrt(a)

    b0 = a * ((a + 1) - (a - 1) * cosw0 + 2 * asquared * alpha)
    b1 = 2 * a * ((a - 1) - (a + 1) * cosw0)
    b2 = a * ((a + 1) - (a - 1) * cosw0 - 2 * asquared * alpha)
    a0 = (a + 1) + (a - 1) * cosw0 + 2 * asquared * alpha
    a1 = -2 * ((a - 1) + (a + 1) * cosw0)
    a2 = (a + 1) + (a - 1) * cosw0 - 2 * asquared * alpha
    return [b0, b1, b2], [a0, a1, a2]


def gen_high_shelf(f0, dbgain, qfactor, fs):
    """Generate high shelving filter coeficcients (digital).
    f0: The frequency where the gain in decibel is at half the maximum value.
       Normalized to sampling frequency, i.e output will be filter from 0 to 2pi.
    dbgain: gain at the top of the shelf in decibels
    qfactor: determines shape of filter TODO: Document better
    fs: sampling frequency

    TODO: Generate based on -3db
    Based on: https://www.w3.org/2011/audio/audio-eq-cookbook.html
    """
    a = 10 ** (dbgain / 40.0)
    w0 = 2 * math.pi * (f0 / fs)
    alpha = math.sin(w0) / (2 * qfactor)

    cosw0 = math.cos(w0)
    asquared = math.sqrt(a)

    b0 = a * ((a + 1) + (a - 1) * cosw0 + 2 * asquared * alpha)
    b1 = -2 * a * ((a - 1) + (a + 1) * cosw0)
    b2 = a * ((a + 1) + (a - 1) * cosw0 - 2 * asquared * alpha)
    a0 = (a + 1) - (a - 1) * cosw0 + 2 * asquared * alpha
    a1 = 2 * ((a - 1) - (a + 1) * cosw0)
    a2 = (a + 1) - (a - 1) * cosw0 - 2 * asquared * alpha
    return [b0, b1, b2], [a0, a1, a2]


def filter_simple(data, filter_coeffs):
    fb, fa = filter_coeffs
    return sps.filtfilt(fb, fa, data, padlen=150)


# def comb_c_pal(data, linelen):
#     """Very basic comb filter, adds the signal together with a signal delayed by 2H,
#     line by line. VCRs do this to reduce crosstalk.
#     """

#     data2 = data.copy()
#     numlines = len(data) // linelen
#     for l in range(16,numlines - 2):
#         delayed2h = data[(l - 2) * linelen:(l - 1) * linelen]
#         data[l * linelen:(l + 1) * linelen] += (delayed2h / 2)
#     return data


def comb_c_ntsc(data, line_len):
    """Very basic comb filter, adds the signal together with a signal delayed by 1H,
    line by line. VCRs do this to reduce crosstalk.
    """

    data2 = data.copy()
    numlines = len(data) // line_len
    for line_num in range(16, numlines - 2):
        delayed1h = data2[(line_num - 1) * line_len : (line_num) * line_len]
        line_slice = data[line_num * line_len : (line_num + 1) * line_len]
        # Let the delayed signal contribute 1/3.
        # Could probably make the filtering configurable later.
        data[line_num * line_len : (line_num + 1) * line_len] = (
            (line_slice * 2) - (delayed1h)
        ) / 3
    return data


def upconvert_chroma(
    chroma,
    lineoffset,
    linesout,
    outwidth,
    chroma_heterodyne,
    phase_rotation,
    starting_phase,
):
    uphet = np.zeros(chroma.size, dtype=np.double)
    if phase_rotation == 0:
        # Track 1 - for PAL, phase doesn't change.
        start = lineoffset
        end = lineoffset + (outwidth * linesout)
        heterodyne = chroma_heterodyne[0][start:end]
        c = chroma[start:end]
        # Mixing the chroma signal with a signal at the frequency of colour under + fsc gives us
        # a signal with frequencies at the difference and sum, the difference is what we want as
        # it's at the right frequency.
        mixed = heterodyne * c

        uphet[start:end] = mixed

    else:
        #        rotation = [(0,0),(90,-270),(180,-180),(270,-90)]
        # Track 2 - needs phase rotation or the chroma will be inverted.
        phase = starting_phase
        for linenumber in range(lineoffset, linesout + lineoffset):
            linestart = (linenumber - lineoffset) * outwidth
            lineend = linestart + outwidth

            heterodyne = chroma_heterodyne[phase][linestart:lineend]

            c = chroma[linestart:lineend]

            line = heterodyne * c

            uphet[linestart:lineend] = line

            phase = (phase + phase_rotation) % 4
    return uphet


def burst_deemphasis(chroma, lineoffset, linesout, outwidth, burstarea):
    for line in range(lineoffset, linesout + lineoffset):
        linestart = (line - lineoffset) * outwidth
        lineend = linestart + outwidth

        chroma[linestart + burstarea[1] + 5 : lineend] *= 2

    return chroma


def process_chroma(field, track_phase, disable_deemph=False):
    # Run TBC/downscale on chroma.
    chroma, _, _ = ldd.Field.downscale(field, channel="demod_burst")

    lineoffset = field.lineoffset + 1
    linesout = field.outlinecount
    outwidth = field.outlinelen

    burstarea = (
        math.floor(field.usectooutpx(field.rf.SysParams["colorBurstUS"][0]) - 5),
        math.ceil(field.usectooutpx(field.rf.SysParams["colorBurstUS"][1])) + 10,
    )

    # For NTSC, the color burst amplitude is doubled when recording, so we have to undo that.
    if field.rf.system == "NTSC" and not disable_deemph:
        chroma = burst_deemphasis(chroma, lineoffset, linesout, outwidth, burstarea)

    # Track 2 is rotated ccw in both NTSC and PAL for VHS
    # u-matic has no phase rotation.
    phase_rotation = -1 if track_phase is not None else 0
    # What phase we start on. (Needed for NTSC to get the color phase correct)
    starting_phase = 0

    if track_phase is not None and field.rf.field_number % 2 == track_phase:
        if field.rf.system == "PAL":
            # For PAL, track 1 has no rotation.
            phase_rotation = 0
        elif field.rf.system == "NTSC":
            # For NTSC, track 1 rotates cw
            phase_rotation = 1
            starting_phase = 1
        else:
            raise Exception("Unknown video system!", field.rf.system)

    uphet = upconvert_chroma(
        chroma,
        lineoffset,
        linesout,
        outwidth,
        field.rf.chroma_heterodyne,
        phase_rotation,
        starting_phase,
    )

    # uphet = comb_c_pal(uphet,outwidth)

    # Filter out unwanted frequencies from the final chroma signal.
    # Mixing the signals will produce waves at the difference and sum of the
    # frequencies. We only want the difference wave which is at the correct color
    # carrier frequency here.
    # We do however want to be careful to avoid filtering out too much of the sideband.
    uphet = filter_simple(uphet, field.rf.Filters["FChromaFinal"])

    # Basic comb filter for NTSC to calm the color a little.
    if field.rf.system == "NTSC":
        uphet = comb_c_ntsc(uphet, outwidth)

    # Final automatic chroma gain.
    uphet = acc(
        uphet,
        field.rf.SysParams["burst_abs_ref"],
        burstarea[0],
        burstarea[1],
        outwidth,
        linesout,
    )

    return uphet


def decode_chroma_vhs(field):
    """Do track detection if needed and upconvert the chroma signal"""
    # Use field number based on raw data position
    # This may not be 100% accurate, so we may want to add some more logic to
    # make sure we re-check the phase occasionally.
    raw_loc = field.rf.decoder.readloc / field.rf.decoder.bytes_per_field

    check_increment_field_no(field.rf)

    # If we moved significantly more than the length of one field, re-check phase
    # as we may have skipped fields.
    if raw_loc - field.rf.last_raw_loc > 2.0:
        if field.rf.detect_track:
            ldd.logger.info("Possibly skipped track, re-checking phase..")
            field.rf.needs_detect

    if field.rf.detect_track and field.rf.needs_detect:
        field.rf.track_phase = field.try_detect_track()
        field.rf.needs_detect = False

    uphet = process_chroma(field, field.rf.track_phase)
    field.uphet_temp = uphet
    # Store previous raw location so we can detect if we moved in the next call.
    field.rf.last_raw_loc = raw_loc
    return chroma_to_u16(uphet)


def decode_chroma_umatic(field):
    """Do track detection if needed and upconvert the chroma signal"""
    # Use field number based on raw data position
    # This may not be 100% accurate, so we may want to add some more logic to
    # make sure we re-check the phase occasionally.
    raw_loc = field.rf.decoder.readloc / field.rf.decoder.bytes_per_field

    check_increment_field_no(field.rf)

    uphet = process_chroma(field, None, True)
    field.uphet_temp = uphet
    # Store previous raw location so we can detect if we moved in the next call.
    field.rf.last_raw_loc = raw_loc
    return chroma_to_u16(uphet)


def get_burst_area(field):
    return (
        math.floor(field.usectooutpx(field.rf.SysParams["colorBurstUS"][0])),
        math.ceil(field.usectooutpx(field.rf.SysParams["colorBurstUS"][1])),
    )


def get_line(data, line_length, line):
    return data[line * line_length : (line + 1) * line_length]


class LineInfo:
    """Helper class to store line burst info for PAL."""

    def __init__(self, num):
        self.linenum = num
        self.bp = 0
        self.bq = 0
        self.vsw = -1
        self.burst_norm = 0

    def __str__(self):
        return "<num: %s, bp: %s, bq: %s, vsw: %s, burst_norm: %s>" % (
            self.linenum,
            self.bp,
            self.bq,
            self.vsw,
            self.burst_norm,
        )


def mean_of_burst_sums(chroma_data, line_length, lines, burst_start, burst_end):
    """Sum the burst areas of two and two lines together, and return the mean of these sums."""
    IGNORED_LINES = 16

    burst_sums = []

    # We ignore the top and bottom 16 lines. The top will typically not have a color burst, and
    # the bottom 16 may be after or at the head switch where the phase rotation will be different.
    start_line = IGNORED_LINES
    end_line = lines - IGNORED_LINES

    for line_number in range(start_line, end_line, 2):
        burst_a = get_line(chroma_data, line_length, line_number)[burst_start:burst_end]
        burst_b = get_line(chroma_data, line_length, line_number + 1)[
            burst_start:burst_end
        ]

        # Use the absolute of the sums to differences cancelling out.
        mean_dev = np.mean(abs(burst_a + burst_b))

        burst_sums.append(mean_dev)

    mean_burst_sum = np.nanmean(burst_sums)
    return mean_burst_sum


def detect_burst_pal(
    chroma_data, sine_wave, cosine_wave, burst_area, line_length, lines
):
    """Decode the burst of most lines to see if we have a valid PAL color burst."""

    # Ignore the first and last 16 lines of the field.
    # first ones contain sync and often doesn't have color burst,
    # while the last lines of the field will contain the head switch and may be distorted.
    IGNORED_LINES = 16
    line_data = []
    burst_norm = np.full(lines, np.nan)
    # Decode the burst vectors on each line and try to get an average of the burst amplitude.
    for linenumber in range(IGNORED_LINES, lines - IGNORED_LINES):
        info = detect_burst_pal_line(
            chroma_data, sine_wave, cosine_wave, burst_area, line_length, linenumber
        )
        line_data.append(info)
        burst_norm[linenumber] = info.burst_norm

    burst_mean = np.nanmean(burst_norm[IGNORED_LINES : lines - IGNORED_LINES])

    return line_data, burst_mean


def detect_burst_pal_line(
    chroma_data, sine, cosine, burst_area, line_length, line_number
):
    """Detect burst function ported from the C++ chroma decoder (palcolour.cpp)

    Tries to decode the PAL chroma vectors from the line's color burst
    """
    empty_line = np.zeros_like(chroma_data[0:line_length])
    num_lines = chroma_data.size / line_length

    # Use an empty line if we try to access outside the field.
    def line_or_empty(line):
        return (
            get_line(chroma_data, line_length, line)
            if line >= 0 and line < num_lines
            else empty_line
        )

    in0 = line_or_empty(line_number)
    in1 = line_or_empty(line_number - 1)
    in2 = line_or_empty(line_number + 1)
    in3 = line_or_empty(line_number - 2)
    in4 = line_or_empty(line_number + 2)
    bp = 0
    bq = 0
    bpo = 0
    bqo = 0

    # (Comment from palcolor.cpp)
    # Find absolute burst phase relative to the reference carrier by
    # product detection.
    #
    # To avoid hue-shifts on alternate lines, the phase is determined by
    # averaging the phase on the current-line with the average of two
    # other lines, one above and one below the current line.
    #
    # For PAL we use the next-but-one line above and below (in the field),
    # which will have the same V-switch phase as the current-line (and 180
    # degree change of phase), and we also analyse the average (bpo/bqo
    # 'old') of the line immediately above and below, which have the
    # opposite V-switch phase (and a 90 degree subcarrier phase shift).
    for i in range(burst_area[0], burst_area[1]):
        bp += ((in0[i] - ((in3[i] + in4[i]) / 2.0)) / 2.0) * sine[i]
        bq += ((in0[i] - ((in3[i] + in4[i]) / 2.0)) / 2.0) * cosine[i]
        bpo += ((in2[i] - in1[i]) / 2.0) * sine[i]
        bqo += ((in2[i] - in1[i]) / 2.0) * cosine[i]

    # (Comment from palcolor.cpp)
    # Normalise the sums above
    burst_length = burst_area[1] - burst_area[0]

    bp /= burst_length
    bq /= burst_length
    bpo /= burst_length
    bqo /= burst_length

    # (Comment from palcolor.cpp)
    # Detect the V-switch state on this line.
    # I forget exactly why this works, but it's essentially comparing the
    # vector magnitude /difference/ between the phases of the burst on the
    # present line and previous line to the magnitude of the burst. This
    # may effectively be a dot-product operation...
    line = LineInfo(line_number)
    if ((bp - bpo) * (bp - bpo) + (bq - bqo) * (bq - bqo)) < (bp * bp + bq * bq) * 2:
        line.vsw = 1

    # (Comment from palcolor.cpp)
    # Average the burst phase to get -U (reference) phase out -- burst
    # phase is (-U +/-V). bp and bq will be of the order of 1000.
    line.bp = (bp - bqo) / 2
    line.bq = (bq + bpo) / 2

    # (Comment from palcolor.cpp)
    # Normalise the magnitude of the bp/bq vector to 1.
    # Kill colour if burst too weak.
    # XXX magic number 130000 !!! check!
    burst_norm = max(math.sqrt(line.bp * line.bp + line.bq * line.bq), 130000.0 / 128)
    line.burst_norm = burst_norm
    line.bp /= burst_norm
    line.bq /= burst_norm

    return line


def detect_burst_ntsc(
    chroma_data, sine_wave, cosine_wave, burst_area, line_length, lines
):
    """Check the phase of the color burst."""

    # Ignore the first and last 16 lines of the field.
    # first ones contain sync and often doesn't have color burst,
    # while the last lines of the field will contain the head switch and may be distorted.
    IGNORED_LINES = 16
    odd_i_acc = 0
    even_i_acc = 0

    for linenumber in range(IGNORED_LINES, lines - IGNORED_LINES):
        bi, _, _ = detect_burst_ntsc_line(
            chroma_data, sine_wave, cosine_wave, burst_area, line_length, linenumber
        )
        #        line_data.append((bi, bq, linenumber))
        if linenumber % 2 == 0:
            even_i_acc += bi
        else:
            odd_i_acc += bi

    num_lines = lines - (IGNORED_LINES * 2)

    return even_i_acc / num_lines, odd_i_acc / num_lines


def detect_burst_ntsc_line(
    chroma_data, sine, cosine, burst_area, line_length, line_number
):
    sf = sine
    cf = cosine

    bi = 0
    bq = 0
    # TODO:
    sine = sine[burst_area[0] :]
    cosine = cosine[burst_area[0] :]
    line = get_line(chroma_data, line_length, line_number)
    for i in range(burst_area[0], burst_area[1]):
        bi += line[i] * sine[i]
        bq += line[i] * cosine[i]

    burst_length = burst_area[1] - burst_area[0]

    bi /= burst_length
    bq /= burst_length

    burst_norm = max(math.sqrt(bi * bi + bq * bq), 130000.0 / 128)
    bi /= burst_norm
    bq /= burst_norm
    return bi, bq, burst_norm


def get_field_phase_id(field):
    """Try to determine which of the 4 NTSC phase cycles the field is.
    For tapes the result seem to not be cyclical at all, not sure if that's normal
    or if something is off.
    The most relevant thing is which lines the burst phase is positive or negative on.
    """
    burst_area = get_burst_area(field)

    sine_wave = field.rf.fsc_wave
    cosine_wave = field.rf.fsc_cos_wave

    # Try to detect the average burst phase of odd and even lines.
    even, odd = detect_burst_ntsc(
        field.uphet_temp,
        sine_wave,
        cosine_wave,
        burst_area,
        field.outlinelen,
        field.outlinecount,
    )

    # This map is based on (first field, field14)
    map4 = {
        (True, True): 1,
        (False, False): 2,
        (True, False): 3,
        (False, True): 4,
    }

    phase_id = map4[(field.isFirstField, even < odd)]

    # ldd.logger.info("Field: %i, Odd I %f , Even I %f, phase id %i, field first %i",
    #                field.rf.field_number, even, odd, phase_id, field.isFirstField)

    return phase_id


def find_crossings(data, threshold):
    """Find where the data crosses the set threshold."""

    # We do this by constructing array where positions above
    # the threshold are marked as true, other sfalse,
    # and use diff to mark where the value changes.
    crossings = np.diff(data < threshold)
    # TODO: See if we can avoid reduntantly looking for both up and
    # down crossing when we just need one of them.
    return crossings


def find_crossings_dir(data, threshold, look_for_down):
    """Find where the data crosses the set threshold
    the look_for_down parameters determines if the crossings returned are down
    or up crossings.
    ."""
    crossings = find_crossings(data, threshold)
    crossings_pos = np.argwhere(crossings)[:, 0]
    if len(crossings_pos) <= 0:
        return []
    first_cross = crossings_pos[0]
    if first_cross >= len(data):
        return []
    first_crossing_is_down = data[first_cross] > data[first_cross + 1]
    if first_crossing_is_down == look_for_down:
        return crossings_pos[::2]
    else:
        return crossings_pos[1::2]


def combine_to_dropouts(crossings_down, crossings_up, merge_threshold):
    """Combine arrays of up and down crossings, and merge ones with small gaps between them.
    Intended to be used where up and down crossing levels are different, the two lists will not
    always alternate or have the same length.
    Returns a list of start/end tuples.
    """
    used = []

    # TODO: Fix when ending on dropout

    cr_up = iter(crossings_up)
    last_u = 0
    # Loop through crossings and combine
    # TODO: Doing this via a loop is probably not ideal in python,
    # we may want to look for a way to more directly generate a list of down/up crossings
    # with hysteresis.
    for d in crossings_down:
        if d < last_u:
            continue

        # If the distance between two dropouts is very small, we merge them.
        if d - last_u < merge_threshold and len(used) > 0:
            # Pop the last added dropout and use it's starting point
            # as the start of the merged one.
            last = used.pop()
            d = last[0]

        for u in cr_up:
            if u > d:
                used.append((d, u))
                last_u = u
                break

    return used


def detect_dropouts_rf(field):
    """Look for dropouts in the input data, based on rf envelope amplitude.
    Uses either an percentage of the frame average rf level, or an absolute value.
    TODO: A more advanced algorithm with hysteresis etc.
    """
    env = field.data["video"]["envelope"]
    threshold_p = field.rf.dod_threshold_p
    threshold_abs = field.rf.dod_threshold_a
    hysteresis = field.rf.dod_hysteresis

    threshold = 0.0
    if threshold_abs is not None:
        threshold = threshold_abs
    else:
        # Generate a threshold based on the field envelope average.
        # This may not be ideal on a field with a lot of droputs,
        # so we may want to use statistics of the previous averages
        # to avoid the threshold ending too low.
        field_average = np.mean(field.data["video"]["envelope"])
        threshold = field_average * threshold_p

    errlist = []

    crossings_down = find_crossings_dir(env, threshold, True)
    crossings_up = find_crossings_dir(env, threshold * hysteresis, False)

    if (
        len(crossings_down) > 0
        and len(crossings_up) > 0
        and crossings_down[0] > crossings_up[0]
        and env[0] < threshold
    ):
        # Handle if we start on a dropout by adding a zero at the start since we won't have any
        # down crossing for it in the data.
        crossings_down = np.concatenate((np.array([0]), crossings_down), axis=None)

    errlist = combine_to_dropouts(
        crossings_down, crossings_up, vhs_formats.DOD_MERGE_THRESHOLD
    )

    # Drop very short dropouts that were not merged.
    # We do this after mergin to avoid removing short consecutive dropouts that
    # could be merged.
    errlist = list(filter(lambda s: s[1] - s[0] > vhs_formats.DOD_MIN_LENGTH, errlist))

    rv_lines = []
    rv_starts = []
    rv_ends = []

    # Convert to tbc positions.
    dropouts = dropout_errlist_to_tbc(field, errlist)
    for r in dropouts:
        rv_lines.append(r[0] - 1)
        rv_starts.append(int(r[1]))
        rv_ends.append(int(r[2]))

    return rv_lines, rv_starts, rv_ends


def dropout_errlist_to_tbc(field, errlist):
    """Convert data from raw data coordinates to tbc coordinates, and splits up
    multi-line dropouts.
    """
    dropouts = []

    if len(errlist) == 0:
        return dropouts

    # Now convert the above errlist into TBC locations
    errlistc = errlist.copy()

    lineoffset = -field.lineoffset

    # Remove dropouts occuring before the start of the frame so they don't
    # cause the rest to be skipped
    curerr = errlistc.pop(0)
    while len(errlistc) > 0 and curerr[0] < field.linelocs[field.lineoffset]:
        curerr = errlistc.pop(0)

    # TODO: This could be reworked to be a bit cleaner and more performant.

    for line in range(field.lineoffset, field.linecount + field.lineoffset):
        while curerr is not None and inrange(
            curerr[0], field.linelocs[line], field.linelocs[line + 1]
        ):
            start_rf_linepos = curerr[0] - field.linelocs[line]
            start_linepos = start_rf_linepos / (
                field.linelocs[line + 1] - field.linelocs[line]
            )
            start_linepos = int(start_linepos * field.outlinelen)

            end_rf_linepos = curerr[1] - field.linelocs[line]
            end_linepos = end_rf_linepos / (
                field.linelocs[line + 1] - field.linelocs[line]
            )
            end_linepos = int(np.round(end_linepos * field.outlinelen))

            first_line = line + 1 + lineoffset

            # If the dropout spans multiple lines, we need to split it up into one for each line.
            if end_linepos > field.outlinelen:
                num_lines = end_linepos // field.outlinelen

                # First line.
                dropouts.append((first_line, start_linepos, field.outlinelen))
                # Full lines in the middle.
                for n in range(num_lines - 1):
                    dropouts.append((first_line + n + 1, 0, field.outlinelen))
                # leftover on last line.
                dropouts.append(
                    (
                        first_line + (num_lines),
                        0,
                        np.remainder(end_linepos, field.outlinelen),
                    )
                )
            else:
                dropouts.append((first_line, start_linepos, end_linepos))

            if len(errlistc):
                curerr = errlistc.pop(0)
            else:
                curerr = None

    return dropouts


# Phase comprensation stuff - needs rework.
# def phase_shift(data, angle):
#     return np.fft.irfft(np.fft.rfft(data) * np.exp(1.0j * angle), len(data)).real


def check_increment_field_no(rf):
    """Increment field number if the raw data location moved significantly since the last call"""
    raw_loc = rf.decoder.readloc / rf.decoder.bytes_per_field

    if rf.last_raw_loc is None:
        rf.last_raw_loc = raw_loc

    if raw_loc > rf.last_raw_loc:
        rf.field_number += 1
    else:
        ldd.logger.info("Raw data loc didn't advance.")


class FieldPALVHS(ldd.FieldPAL):
    def __init__(self, *args, **kwargs):
        super(FieldPALVHS, self).__init__(*args, **kwargs)

    def refine_linelocs_pilot(self, linelocs=None):
        """Override this as it's LD specific"""
        if linelocs is None:
            linelocs = self.linelocs2.copy()
        else:
            linelocs = linelocs.copy()

        return linelocs

    def downscale(self, final=False, *args, **kwargs):
        dsout, dsaudio, dsefm = super(FieldPALVHS, self).downscale(
            final, *args, **kwargs
        )
        dschroma = decode_chroma_vhs(self)

        return (dsout, dschroma), dsaudio, dsefm

    def calc_burstmedian(self):
        # Set this to a constant value for now to avoid the comb filter messing with chroma levels.
        return 1.0

    def try_detect_track(self):
        """Try to detect what video track we are on.

        VHS tapes have two tracks with different azimuth that alternate and are read by alternating
        heads on the video drum. The phase of the color heterodyne varies depending on what track is
        being read from to avoid chroma crosstalk.
        Additionally, most tapes are recorded with a luma half-shift which shifts the fm-encoded
        luma frequencies slightly depending on the track to avoid luma crosstalk.
        """
        ldd.logger.info("Trying to detect track phase...")
        burst_area = (
            math.floor(self.usectooutpx(self.rf.SysParams["colorBurstUS"][0])),
            math.ceil(self.usectooutpx(self.rf.SysParams["colorBurstUS"][1])),
        )

        # Upconvert chroma twice, once for each possible track phase
        uphet = [process_chroma(self, 0), process_chroma(self, 1)]

        sine_wave = self.rf.fsc_wave
        cosine_wave = self.rf.fsc_cos_wave

        # Try to decode the color burst from each of the upconverted chroma signals
        phase0, phase0_mean = detect_burst_pal(
            uphet[0],
            sine_wave,
            cosine_wave,
            burst_area,
            self.outlinelen,
            self.outlinecount,
        )
        phase1, phase1_mean = detect_burst_pal(
            uphet[1],
            sine_wave,
            cosine_wave,
            burst_area,
            self.outlinelen,
            self.outlinecount,
        )

        # We use the one where the phase of the chroma vectors make the most sense.
        assumed_phase = int(phase0_mean < phase1_mean)

        ldd.logger.info("Phase previously set: %i", self.rf.track_phase)
        ldd.logger.info("phase0 mean: %d", phase0_mean)
        ldd.logger.info("phase1 mean: %d", phase1_mean)
        ldd.logger.info("assumed_phase: %d", assumed_phase)

        return assumed_phase

    def determine_field_number(self):
        """Workaround to shut down phase id mismatch warnings, the actual code
        doesn't work properly with the vhs output at the moment."""
        return 1 + (self.rf.field_number % 8)

    def getpulses(self):
        """Find sync pulses in the demodulated video sigal

        NOTE: TEMPORARY override until an override for the value itself is added upstream.
        """
        # pass one using standard levels

        # pulse_hz range:  vsync_ire - 10, maximum is the 50% crossing point to sync
        pulse_hz_min = self.rf.iretohz(self.rf.SysParams["vsync_ire"] - 10)
        pulse_hz_max = self.rf.iretohz(self.rf.SysParams["vsync_ire"] / 2)

        pulses = lddu.findpulses(
            self.data["video"]["demod_05"], pulse_hz_min, pulse_hz_max
        )

        if len(pulses) == 0:
            # can't do anything about this
            return pulses

        # determine sync pulses from vsync
        vsync_locs = []
        vsync_means = []

        for i, p in enumerate(pulses):
            if p.len > self.usectoinpx(10):
                vsync_locs.append(i)
                vsync_means.append(
                    np.mean(
                        self.data["video"]["demod_05"][
                            int(p.start + self.rf.freq) : int(
                                p.start + p.len - self.rf.freq
                            )
                        ]
                    )
                )

        if len(vsync_means) == 0:
            return None

        synclevel = np.median(vsync_means)

        if np.abs(self.rf.hztoire(synclevel) - self.rf.SysParams["vsync_ire"]) < 5:
            # sync level is close enough to use
            return pulses

        if vsync_locs is None or not len(vsync_locs):
            return None

        # Now compute black level and try again

        # take the eq pulses before and after vsync
        r1 = range(vsync_locs[0] - 5, vsync_locs[0])
        r2 = range(vsync_locs[-1] + 1, vsync_locs[-1] + 6)

        black_means = []

        for i in itertools.chain(r1, r2):
            if i < 0 or i >= len(pulses):
                continue

            p = pulses[i]
            if inrange(p.len, self.rf.freq * 0.75, self.rf.freq * 3):
                black_means.append(
                    np.mean(
                        self.data["video"]["demod_05"][
                            int(p.start + (self.rf.freq * 5)) : int(
                                p.start + (self.rf.freq * 20)
                            )
                        ]
                    )
                )

        blacklevel = np.median(black_means)

        pulse_hz_min = synclevel - (self.rf.SysParams["hz_ire"] * 10)
        pulse_hz_max = (blacklevel + synclevel) / 2

        return lddu.findpulses(
            self.data["video"]["demod_05"], pulse_hz_min, pulse_hz_max
        )

    def compute_deriv_error(self, linelocs, baserr):
        """Disabled this for now as tapes have large variations in line pos
        Due to e.g head switch.
        compute errors based off the second derivative - if it exceeds 1 something's wrong,
        and if 4 really wrong...
        """
        return baserr

    def dropout_detect(self):
        return detect_dropouts_rf(self)


class FieldNTSCVHS(ldd.FieldNTSC):
    def __init__(self, *args, **kwargs):
        super(FieldNTSCVHS, self).__init__(*args, **kwargs)
        self.fieldPhaseID = 0

    def refine_linelocs_burst(self, linelocs=None):
        """Override this as it's LD specific
        At some point in the future we could maybe use the burst location to improve hsync accuracy,
        but ignore it for now.
        """
        if linelocs is None:
            linelocs = self.linelocs2
        else:
            linelocs = linelocs.copy()

        return linelocs

    def calc_burstmedian(self):
        # Set this to a constant value for now to avoid the comb filter messing with chroma levels.
        return 1.0

    def try_detect_track(self):
        """Try to detect which track the current field was read from.
        returns 0 or 1 depending on detected track phase.

        We use the fact that the color burst in NTSC is inverted on every line, so
        in a perfect signal, the burst from one line and the previous one should cancel
        each other out when summed together. When upconverting with the wrong phase rotation,
        the bursts will have the same phase instead, and thus the mean absolute
        sum will be much higher. This seem to give a reasonably good guess, but could probably
        be improved.
        """
        ldd.logger.info("Trying to detect track phase...")
        burst_area = (
            math.floor(self.usectooutpx(self.rf.SysParams["colorBurstUS"][0])),
            math.ceil(self.usectooutpx(self.rf.SysParams["colorBurstUS"][1])),
        )

        # Upconvert chroma twice, once for each possible track phase
        uphet = [process_chroma(self, 0, True), process_chroma(self, 1, True)]

        # Look at the bursts from each upconversion and see which one looks most
        # normal.
        burst_mean_sum_0 = mean_of_burst_sums(
            uphet[0], self.outlinelen, self.outlinecount, burst_area[0], burst_area[1]
        )

        burst_mean_sum_1 = mean_of_burst_sums(
            uphet[1], self.outlinelen, self.outlinecount, burst_area[0], burst_area[1]
        )

        assumed_phase = int(burst_mean_sum_1 < burst_mean_sum_0)

        ldd.logger.info("burst mean sum 0: %f", burst_mean_sum_0)
        ldd.logger.info("burst mean sum 1: %f", burst_mean_sum_1)
        ldd.logger.info("assumed phase: %i", assumed_phase)

        return assumed_phase

    def downscale(self, linesoffset=0, final=False, *args, **kwargs):
        """Downscale the channels and upconvert chroma to standard color carrier frequency."""
        dsout, dsaudio, dsefm = super(FieldNTSCVHS, self).downscale(
            linesoffset, final, *args, **kwargs
        )

        dschroma = decode_chroma_vhs(self)

        self.fieldPhaseID = get_field_phase_id(self)

        return (dsout, dschroma), dsaudio, dsefm

    def dropout_detect(self):
        return detect_dropouts_rf(self)

    def compute_deriv_error(self, linelocs, baserr):
        """Disabled this for now as line starts can vary widely."""
        return baserr


class FieldNTSCUMatic(ldd.FieldNTSC):
    def __init__(self, *args, **kwargs):
        super(FieldNTSCUMatic, self).__init__(*args, **kwargs)
        self.fieldPhaseID = 0

    def refine_linelocs_burst(self, linelocs=None):
        """Override this as it's LD specific
        At some point in the future we could maybe use the burst location to improve hsync accuracy,
        but ignore it for now.
        """
        if linelocs is None:
            linelocs = self.linelocs2
        else:
            linelocs = linelocs.copy()

        return linelocs

    def calc_burstmedian(self):
        # Set this to a constant value for now to avoid the comb filter messing with chroma levels.
        return 1.0

    def downscale(self, linesoffset=0, final=False, *args, **kwargs):
        dsout, dsaudio, dsefm = super(FieldNTSCUMatic, self).downscale(
            linesoffset, final, *args, **kwargs
        )
        dschroma = decode_chroma_umatic(self)

        self.fieldPhaseID = self.fieldPhaseID = get_field_phase_id(self)

        return (dsout, dschroma), dsaudio, dsefm

    def dropout_detect(self):
        return detect_dropouts_rf(self)

    def compute_deriv_error(self, linelocs, baserr):
        """Disabled this for now as line starts can vary widely."""
        return baserr


# Superclass to override laserdisc-specific parts of ld-decode with stuff that works for VHS
#
# We do this simply by using inheritance and overriding functions. This results in some redundant
# work that is later overridden, but avoids altering any ld-decode code to ease merging back in
# later as the ld-decode is in flux at the moment.
class VHSDecode(ldd.LDdecode):
    def __init__(
        self,
        fname_in,
        fname_out,
        freader,
        logger,
        system="NTSC",
        tape_format="VHS",
        doDOD=True,
        threads=1,
        inputfreq=40,
        dod_threshold_p=vhs_formats.DEFAULT_THRESHOLD_P_DDD,
        dod_threshold_a=None,
        dod_hysteresis=vhs_formats.DEFAULT_HYSTERESIS,
        track_phase=0,
        level_adjust=0.2,
    ):
        super(VHSDecode, self).__init__(
            fname_in,
            fname_out,
            freader,
            logger,
            analog_audio=False,
            system=system,
            doDOD=doDOD,
            threads=threads,
        )
        # Adjustment for output to avoid clipping.
        self.level_adjust = level_adjust
        # Overwrite the rf decoder with the VHS-altered one
        self.rf = VHSRFDecode(
            system=system,
            tape_format=tape_format,
            inputfreq=inputfreq,
            track_phase=track_phase,
            dod_threshold_p=dod_threshold_p,
            dod_threshold_a=dod_threshold_a,
            dod_hysteresis=dod_hysteresis,
        )
        # Store reference to ourself in the rf decoder - needed to access data location for track
        # phase, may want to do this in a better way later.
        self.rf.decoder = self
        if system == "PAL":
            self.FieldClass = FieldPALVHS
        elif system == "NTSC":
            if tape_format == "UMATIC":
                self.FieldClass = FieldNTSCUMatic
            else:
                self.FieldClass = FieldNTSCVHS
        else:
            raise Exception("Unknown video system!", system)

        self.demodcache = VTRDemodCache(
            self.rf, self.infile, self.freader, num_worker_threads=self.numthreads
        )

        if fname_out is not None:
            self.outfile_chroma = open(fname_out + "_chroma.tbc", "wb")
        else:
            self.outfile_chroma = None

    # Override to avoid NaN in JSON.
    def calcsnr(self, f, snrslice):
        data = f.output_to_ire(f.dspicture[snrslice])

        signal = np.mean(data)
        noise = np.std(data)

        # Make sure signal is positive so we don't try to do log on a negative value.
        if signal < 0.0:
            ldd.logger.info(
                "WARNING: Negative mean for SNR, changing to absolute value."
            )
            signal = abs(signal)
        if noise == 0:
            return 0
        return 20 * np.log10(signal / noise)

    def calcpsnr(self, f, snrslice):
        data = f.output_to_ire(f.dspicture[snrslice])

        #        signal = np.mean(data)
        noise = np.std(data)
        if noise == 0:
            return 0
        return 20 * np.log10(100 / noise)

    def buildmetadata(self, f):
        if math.isnan(f.burstmedian):
            f.burstmedian = 0.0
        return super(VHSDecode, self).buildmetadata(f)

    # For laserdisc this decodes frame numbers from VBI metadata, but there won't be such a thing on
    # VHS, so just skip it.
    def decodeFrameNumber(self, f1, f2):
        return None

    # Again ignored for tapes
    def checkMTF(self, field, pfield=None):
        return True

    def writeout(self, dataset):
        f, fi, (picturey, picturec), audio, efm = dataset

        fi["audioSamples"] = 0
        self.fieldinfo.append(fi)

        self.outfile_video.write(picturey)
        self.outfile_chroma.write(picturec)
        self.fields_written += 1

    def close(self):
        setattr(self, "outfile_chroma", None)
        super(VHSDecode, self).close()

    def computeMetricsNTSC(self, metrics, f, fp=None):
        return None

    def build_json(self, f):
        jout = super(VHSDecode, self).build_json(f)
        black = jout["videoParameters"]["black16bIre"]
        white = jout["videoParameters"]["white16bIre"]

        jout["videoParameters"]["black16bIre"] = black * (1 - self.level_adjust)
        jout["videoParameters"]["white16bIre"] = white * (1 + self.level_adjust)
        return jout


class VTRDemodCache(ldd.DemodCache):
    def __init__(self,
                 rf,
                 infile,
                 loader,
                 cachesize=256,
                 num_worker_threads=1,
                 MTF_tolerance=0.05):

        super(VTRDemodCache, self).__init__(
            rf,
            infile,
            loader,
            cachesize,
            -1,
            MTF_tolerance
        )
        self.is_vtr = True
        self.zmq_out = None  # it will be initialized at worker side
        self.zmq_in = None

    def worker(self, pipein):
        try:
            self.zmq_out = zm.ZMQSend()
            self.zmq_in = zm.ZMQReceive(port=5566)
        except zmq.error.ZMQError as e:
            print('Cannot initialize zmq_worker %s' % e)

        while True:
            ispiped = False
            if pipein.poll():
                item = pipein.recv()
                ispiped = True
            else:
                item = self.q_in.get()

            if item is None or item[0] == "END":
                return

            if item[0] == "DEMOD":
                blocknum, block, target_MTF = item[1:]

                output = {}

                if "fft" not in block:
                    output["fft"] = npfft.fft(block["rawinput"])
                    fftdata = output["fft"]
                else:
                    fftdata = block["fft"]

                if (
                    "demod" not in block
                    or np.abs(block["MTF"] - target_MTF) > self.MTF_tolerance
                ):
                    output["demod"] = self.rf.demodblock(data=block["rawinput"],
                        fftdata=fftdata, mtf_level=target_MTF, cut=True,
                        zmqio=(self.zmq_out, self.zmq_in)
                    )
                    output["MTF"] = target_MTF

                self.q_out.put((blocknum, output))
            elif item[0] == "NEWPARAMS":
                self.apply_newparams(item[1])

            if not ispiped:
                self.q_in.task_done()


class VHSRFDecode(ldd.RFDecode):
    def __init__(
        self,
        inputfreq=40,
        system="NTSC",
        tape_format="VHS",
        dod_threshold_p=vhs_formats.DEFAULT_THRESHOLD_P_DDD,
        dod_threshold_a=None,
        dod_hysteresis=vhs_formats.DEFAULT_HYSTERESIS,
        track_phase=None,
    ):

        # First init the rf decoder normally.
        super(VHSRFDecode, self).__init__(
            inputfreq, system, decode_analog_audio=False, has_analog_audio=False
        )

        self.dod_threshold_p = dod_threshold_p
        self.dod_threshold_a = dod_threshold_a
        self.dod_hysteresis = dod_hysteresis

        if track_phase is None:
            self.track_phase = 0
            self.detect_track = True
            self.needs_detect = True
        elif track_phase == 0 or track_phase == 1:
            self.track_phase = track_phase
            self.detect_track = False
            self.needs_detect = False
        else:
            raise Exception("Track phase can only be 0, 1 or None")
        self.hsync_tolerance = 0.8

        self.field_number = 0
        self.last_raw_loc = None

        # Then we override the laserdisc parameters with VHS ones.
        if system == "PAL":
            # Give the decoder it's separate own full copy to be on the safe side.
            self.SysParams = copy.deepcopy(vhs_formats.SysParams_PAL_VHS)
            self.DecoderParams = copy.deepcopy(vhs_formats.RFParams_PAL_VHS)
        elif system == "NTSC":
            if tape_format == "UMATIC":
                self.SysParams = copy.deepcopy(vhs_formats.SysParams_NTSC_UMATIC)
                self.DecoderParams = copy.deepcopy(vhs_formats.RFParams_NTSC_UMATIC)
            else:
                self.SysParams = copy.deepcopy(vhs_formats.SysParams_NTSC_VHS)
                self.DecoderParams = copy.deepcopy(vhs_formats.RFParams_NTSC_VHS)
        else:
            raise Exception("Unknown video system! ", system)

        # Lastly we re-create the filters with the new parameters.
        self.computevideofilters()

        cc = self.DecoderParams["color_under_carrier"] / 1000000

        DP = self.DecoderParams

        self.Filters["RFVideoRaw"] = lddu.filtfft(
            sps.butter(
                DP["video_bpf_order"],
                [
                    DP["video_bpf_low"] / self.freq_hz_half,
                    DP["video_bpf_high"] / self.freq_hz_half,
                ],
                btype="bandpass",
            ),
            self.blocklen,
        )

        self.Filters["EnvLowPass"] = sps.butter(
            8, [1.0 / self.freq_half], btype="lowpass"
        )

        # More advanced rf filter - only used for NTSC for now.
        if system == "NTSC":
            y_fm = sps.butter(
                DP["video_bpf_order"],
                [
                    DP["video_bpf_low"] / self.freq_hz_half,
                    DP["video_bpf_high"] / self.freq_hz_half,
                ],
                btype="bandpass",
            )
            y_fm = lddu.filtfft(y_fm, self.blocklen)

            y_fm_lowpass = lddu.filtfft(
                sps.butter(
                    DP["video_lpf_extra_order"],
                    [DP["video_lpf_extra"] / self.freq_hz_half],
                    btype="lowpass",
                ),
                self.blocklen,
            )

            y_fm_chroma_trap = lddu.filtfft(
                sps.butter(
                    1,
                    [(cc * 0.9) / self.freq_half, (cc * 1.1) / self.freq_half],
                    btype="bandstop",
                ),
                self.blocklen,
            )

            y_fm_filter = (
                y_fm * y_fm_lowpass * y_fm_chroma_trap * self.Filters["hilbert"]
            )

            self.Filters["RFVideo"] = y_fm_filter
        else:
            y_fm_lowpass = lddu.filtfft(
                sps.butter(
                    DP["video_lpf_extra_order"],
                    [DP["video_lpf_extra"] / self.freq_hz_half],
                    btype="lowpass",
                ),
                self.blocklen,
            )
            y_fm_highpass = lddu.filtfft(
                sps.butter(
                    DP["video_hpf_extra_order"],
                    [DP["video_hpf_extra"] / self.freq_hz_half],
                    btype="highpass",
                ),
                self.blocklen,
            )
            self.Filters["RFVideo"] = (
                self.Filters["RFVideo"] * y_fm_lowpass * y_fm_highpass
            )

        # Video (luma) de-emphasis
        # Not sure about the math of this but, by using a high-shelf filter and then
        # swapping b and a we get a low-shelf filter that goes from 0 to -14 dB rather
        # than from 14 to 0 which the high shelf function gives.
        da, db = gen_high_shelf(
            DP["deemph_corner"] / 1.0e6, DP["deemph_gain"], 1 / 2, inputfreq
        )
        w, h = sps.freqz(db, da)

        self.Filters["Fdeemp"] = lddu.filtfft((db, da), self.blocklen)
        self.Filters["FVideo"] = self.Filters["Fvideo_lpf"] * self.Filters["Fdeemp"]
        SF = self.Filters
        SF["FVideo05"] = SF["Fvideo_lpf"] * SF["Fdeemp"] * SF["F05"]

        # Filter to pick out color-under chroma component.
        # filter at about twice the carrier. (This seems to be similar to what VCRs do)
        # TODO: Needs tweaking
        # Note: order will be doubled since we use filtfilt.
        chroma_lowpass = sps.butter(
            4, [0.05 / self.freq_half, 1.4 / self.freq_half], btype="bandpass"
        )  # sps.butter(4, [1.2/self.freq_half], btype='lowpass')
        self.Filters["FVideoBurst"] = chroma_lowpass

        # The following filters are for post-TBC:
        # The output sample rate is at approx 4fsc
        fsc_mhz = self.SysParams["fsc_mhz"]
        out_sample_rate_mhz = fsc_mhz * 4
        out_frequency_half = out_sample_rate_mhz / 2
        fieldlen = self.SysParams["outlinelen"] * max(self.SysParams["field_lines"])

        # Final band-pass filter for chroma output.
        # Mostly to filter out the higher-frequency wave that results from signal mixing.
        # Needs tweaking.
        # Note: order will be doubled since we use filtfilt.
        chroma_bandpass_final = sps.butter(
            2,
            [
                (fsc_mhz - 0.64) / out_frequency_half,
                (fsc_mhz + 0.24) / out_frequency_half,
            ],
            btype="bandpass",
        )
        self.Filters["FChromaFinal"] = chroma_bandpass_final

        chroma_burst_check = sps.butter(
            2,
            [
                (fsc_mhz - 0.14) / out_frequency_half,
                (fsc_mhz + 0.04) / out_frequency_half,
            ],
            btype="bandpass",
        )
        self.Filters["FChromaBurstCheck"] = chroma_burst_check

        samples = np.arange(fieldlen)

        # Standard frequency color carrier wave.
        self.fsc_wave = utils.gen_wave_at_frequency(
            fsc_mhz, out_sample_rate_mhz, fieldlen
        )
        self.fsc_cos_wave = utils.gen_wave_at_frequency(
            fsc_mhz, out_sample_rate_mhz, fieldlen, np.cos
        )

        # Heterodyne wave
        # We combine the color carrier with a wave with a frequency of the
        # subcarrier + the downconverted chroma carrier to get the original
        # color wave back.
        het_freq = fsc_mhz + cc
        cc_wave_scale = het_freq / out_sample_rate_mhz
        self.cc_ratio = cc_wave_scale
        # 0 phase downconverted color under carrier wave
        self.cc_wave = np.sin(2 * np.pi * cc_wave_scale * samples)

        Fc_half_pi = round(out_sample_rate_mhz / (4 * cc))
        carrier = deque(self.cc_wave)
        carrier.rotate(Fc_half_pi)
        phase_90 = np.asarray(carrier)
        carrier.rotate(Fc_half_pi)
        phase_180 = np.asarray(carrier)
        carrier.rotate(Fc_half_pi)
        phase_270 = np.asarray(carrier)
        self.chroma_heterodyne = {
            0: self.cc_wave,
            1: phase_90,
            2: phase_180,
            3: phase_270
        }
        self.int_amplitude = list()
        self.ext_amplitude = list()
        self.int_min = list()
        self.min_ext_demod = list()
        self.min_demod = list()
        yiir_b, yiir_a = utils.firdes_lowpass(self.freq_hz, 2.7e6, 800e3, order_limit=20)
        fmhipass = utils.firdes_highpass(self.freq_hz, 2.4e6, 500e3, order_limit=20)
        fmlopass = utils.firdes_lowpass(self.freq_hz, 6.4e6, 3e6, order_limit=20)
        #fmhipass = utils.firdes_highpass(self.freq_hz, 3490000, 500e3, order_limit=1)
        #fmlopass = utils.firdes_lowpass(self.freq_hz, 5580000, 3e6, order_limit=1)

        self.luma_limit = utils.FiltersClass(yiir_b, yiir_a, self.freq_hz)
        self.YFM_filter = {
            0: utils.FiltersClass(fmhipass[0], fmhipass[1], self.freq_hz),
            1: utils.FiltersClass(fmlopass[0], fmlopass[1], self.freq_hz),
        }
        self.dtw = dtw.TimeWarper(self.DecoderParams["color_under_carrier"],
                                  self.SysParams["FPS"] * 2,
                                  self.freq_hz)
        self.cdtw = dtw.TimeWarper(self.DecoderParams["color_under_carrier"],
                                  self.SysParams["FPS"] * 2,
                                  self.freq_hz)
        #utils.filter_plot(fmhipass[0], fmhipass[1], self.freq_hz, 'highpass', 'FM highpass')
        #utils.filter_plot(fmlopass[0], fmlopass[1], self.freq_hz, 'lowpass', 'FM lowpass')
        self.zeroblock = np.zeros(pow(2,15))
        print('Set samplerate at: %d Hz' % self.freq_hz)

    def computedelays(self, mtf_level=0):
        """Override computedelays
        It's normally used for dropout compensation, but the dropout compensation implementation
        in ld-decode assumes composite color. This function is called even if it's disabled, and
        seems to break with the VHS setup, so we disable it by overriding it for now.
        """
        # Set these to 0 for now, the metrics calculations look for them.
        self.delays = {}
        self.delays["video_sync"] = 0
        self.delays["video_white"] = 0

    def external_demod(self, zmqio, rf, manual_gain=1.0):
        ## pipes to external demod
        zmq_out = zmqio[0]
        zmq_in = zmqio[1]
        out_samples = len(rf)
        zmq_out.send_complex(rf)

        demod = zmq_in.receive(out_samples)

        # DC removes using a moving average
        # it will take a complete frame to stabilize
        self.min_ext_demod.append(min(demod))
        demod -= utils.moving_average(self.min_ext_demod, window=self.SysParams["frame_lines"])

        out_video = np.round(
            self.iretohz(self.SysParams["vsync_ire"]) + (
                    demod * manual_gain * self.iretohz(100) / 28
            )
        ).astype(np.int)

        assert len(out_video) == out_samples, \
            'Something gone wrong at external demod, expected samples %d, received %d' % (len(out_video), out_samples)

        demod_fft = np.fft.fft(out_video)
        #out_video = self.YNR(out_video)

        return out_video, demod_fft, out_video

    def hilbert_demod(self, data):

        #hi = self.YFM_filter[0].work(data)
        #pre_filtered = self.YFM_filter[1].work(hi)
        fftdata = np.fft.fft(data)
        indata_fft_filt = fftdata * self.Filters["RFVideo"]
        rf_filtered = np.fft.ifft(indata_fft_filt)
        demod = unwrap_hilbert(rf_filtered, self.freq_hz)
        demod_fft = np.fft.fft(demod)
        out_video = np.fft.ifft(demod_fft * self.Filters["FVideo"]).real

        return demod, demod_fft, out_video


    def do_emd(self, x):
        from pyhht.visualization import plot_imfs
        import matplotlib.pyplot as plt
        t = np.linspace(0, 1, len(x))
        decomposer = EMD(x, maxiter=3000, n_imfs=3)
        imfs = decomposer.decompose()
        #plt.plot(imfs[0], t)
        #plt.show()
        #plot_imfs(x, imfs, t)
        imfsum = np.zeros(len(imfs[0]))
        for i in range(0, min(imfs.shape[0], 3)):
            imfsum = np.add(imfsum, imfs[i])
        return imfsum

    def alt_fm_demod(self, data):
        demod, t = inst_freq(data)
        demod = np.append(demod, np.zeros(2))
        demod = np.add(np.multiply(demod, -self.freq_hz), self.freq_hz / 2)
        return demod

    def hilbert_huang_demod(self, data):

        # second RF AFE filter
        hi = self.YFM_filter[0].workl(data)
        rf_filtered = self.YFM_filter[1].workl(hi)

        #First RF filter AFE
        fftdata = np.fft.fft(rf_filtered)
        indata_fft_filt = fftdata * self.Filters["RFVideo"]
        rf_filtered = np.fft.ifft(indata_fft_filt)

        #imfs = self.do_emd(rf_filtered.real)
        #hht_fft = np.fft.fft(imf0)
        #indata_fft_filt = hht_fft * self.Filters["RFVideo"]
        #out_samples = len(data)


        #imfs = self.do_emd(rf_filtered.real) #+ 1j * self.do_emd(rf_filtered.imag)

        #FM demod
        demod = self.alt_fm_demod(rf_filtered.real)

        #alt_demod = unwrap_hilbert(imfs, self.freq_hz)

        #DC removal
        self.min_demod.append(min(demod))
        demod -= utils.moving_average(self.min_demod, window=self.SysParams["frame_lines"])
        #demod += self.iretohz(self.SysParams["vsync_ire"]) / 2

        #alt_demod -= utils.moving_average(self.min_ext_demod, window=self.SysParams["frame_lines"])


        demod_fft = np.fft.fft(demod)
        out_video = np.fft.ifft(demod_fft * self.Filters["FVideo"]).real
        #out_video = self.YNR(out_video)
        out_video = self.luma_limit.work(out_video)
        #assert len(out_video) == out_samples
        return demod, demod_fft, out_video


    def amplitude_log(self, ext_video, int_video):
        print('-> min int %d, max int %d :: min ext %d, max ext %d' % (
              min(int_video), max(int_video),
              min(ext_video), max(ext_video)
            )
        )

        self.int_min.append(min(int_video))
        int_amplitude = max(int_video) - min(int_video)
        ext_amplitude = max(ext_video) - min(ext_video)
        self.int_amplitude.append(int_amplitude)
        self.ext_amplitude.append(ext_amplitude)
        print('->> amp int %.3f :: amp ext %.3f :: min int %.3f' % (
            sum(self.int_amplitude) / len(self.int_amplitude),
            sum(self.ext_amplitude) / len(self.ext_amplitude),
            sum(self.int_min) / len(self.int_min)
            )
        )

    # It resamples the luminance data to 4 * Fc
    # Applies the comb filter, then resamples it back
    # The converter params are the same as in libsamplerate:
    # In ascending quality/complexity order:
    #   zero_order_hold, linear, sinc_fastest, sinc_best
    def YNR(self, luminance, converter='linear', delay=-2):
        quotients_limit = int(1e4)
        Fc = int(self.SysParams["fsc_mhz"] * 4 * 1e6)
        ratio = Fraction(Fc/self.freq_hz).limit_denominator(quotients_limit)
        dw_ratio = ratio.numerator / ratio.denominator
        up_ratio = ratio.denominator / ratio.numerator
        downsampled = resample(luminance, ratio=dw_ratio, converter_type=converter)
        delayed = deque(downsampled.copy())
        delayed.rotate(delay)
        combed = np.multiply(np.add(downsampled, np.asarray(delayed)), 0.5)
        result = resample(combed, ratio=up_ratio, converter_type=converter)
        """
        if len(luminance) > len(result):
            err = len(luminance) - len(result)
            result = np.append(result, luminance[len(luminance) - err: len(luminance)])
        else:
            result = result[:len(luminance)]
        """
        result = utils.pad_or_truncate(result, luminance)
        assert len(luminance) == len(result), \
            'Something wrong happened during the comb filtering stage. Expected samples %d, got %d' % \
            (len(luminance), len(result))
        return result

    def demodblock(self, data=None, mtf_level=0, fftdata=None, cut=False, zmqio=(None, None), amp_comp=True):
        rv = {}
        #rdata, stats = self.dtw.velocity_compensator(data)
        #data = utils.pad_or_truncate(rdata, data)
        #fftdata = np.fft.fft(data[: self.blocklen])

        resampled = self.cdtw.velocity_compensator(data)
        hsj = self.dtw.head_switch_jitter(resampled)
        zmqio[0].send_complex(
            hsj[0] + 1j * hsj[1]
        )
        data = resampled
        indata_fft = np.fft.fft(data[: self.blocklen])

        #if fftdata is not None:
        #    indata_fft = fftdata
        #elif data is not None:
        #    indata_fft = np.fft.fft(data[: self.blocklen])
        #else:
        #    raise Exception("demodblock called without raw or FFT data")

        #if data is None:
        #    data = np.fft.ifft(indata_fft).real

        # switches between internal demodulator and the external one
        if zmqio[0] is None:
            demod, demod_fft, out_video = self.hilbert_demod(indata_fft)
        else:
            #indata_fft_filt = indata_fft * self.Filters["RFVideo"]
            #rf_filtered = np.fft.ifft(indata_fft_filt)
            #demod, demod_fft, int_video = self.external_demod(zmqio, rf_filtered)
            if amp_comp:
                _, _, int_video = self.hilbert_demod(data)
                demod, demod_fft, out_video = self.hilbert_huang_demod(data)
                # assert not np.isnan(out_video).any() and not np.isnan(out_chroma).any(), 'Got NAN at demodblock()'
                # assert len(out_video) == len(self.zeroblock)
                # print('After max:', min(out_video), max(out_video))

                self.amplitude_log(out_video, int_video)

        out_video05 = np.fft.ifft(demod_fft * self.Filters["FVideo05"]).real
        out_video05 = np.roll(out_video05, -self.Filters["F05_offset"])

        # Filter out the color-under signal from the raw data.
        out_chroma = filter_simple(data[: self.blocklen], self.Filters["FVideoBurst"])

        # Move chroma to compensate for Y filter delay.
        # value needs tweaking, ideally it should be calculated if possible.
        # TODO: Not sure if we need this after hilbert filter change, needs check.
        out_chroma = np.roll(out_chroma, 10)
        # crude DC offset removal
        out_chroma = out_chroma - np.mean(out_chroma)

        from scipy.signal import hilbert as hilbt

        raw_filtered = np.fft.ifft(indata_fft * self.Filters["RFVideoRaw"]).real
        # Calculate an evelope with signal strength using absolute of hilbert transform.
        env = np.abs(hilbt(raw_filtered))

        assert len(out_video) == pow(2, 15), 'Unexpected uneven block'

        if True:
            import matplotlib.pyplot as plt

            fig, ax1 = plt.subplots()
            # ax1.plot((20 * np.log10(self.Filters["Fdeemp"])))
            #        ax1.plot(hilbert, color='#FF0000')
            # ax1.plot(data, color="#00FF00")
            ax1.axhline(self.iretohz(0))
            ax1.axhline(self.iretohz(self.SysParams["vsync_ire"]))
            ax1.axhline(self.iretohz(7.5))
            ax1.axhline(self.iretohz(100))
            # print("Vsync IRE", self.SysParams["vsync_ire"])
            #            ax2 = ax1.twinx()
            #            ax3 = ax1.twinx()
            if zmqio[0] is not None:
                ax1.plot(out_video[:4096], color="#FF0000")
                #ax1.plot(int_video[:4096], color="#0000FF")
            else:
                ax1.plot(out_video, color="#FF0000")
            #            crossings = find_crossings(env, 700)
            #            ax3.plot(crossings, color="#0000FF")
            plt.show()

        # demod_burst is a bit misleading, but keeping the naming for compatability.
        video_out = np.rec.array(
            [out_video, demod, out_video05, out_chroma, env, data],
            names=["demod", "demod_raw", "demod_05", "demod_burst", "envelope", "raw"],
        )

        rv["video"] = (
            video_out[self.blockcut : -self.blockcut_end] if cut else video_out
        )

        return rv
